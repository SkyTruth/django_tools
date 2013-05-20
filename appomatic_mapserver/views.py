import django.template
import django.shortcuts
import django.http
import fcdjangoutils.jsonview
import django.db
import contextlib
import datetime
import shapely.geometry
import shapely.wkb
import shapely.wkt
import fastkml.kml
import geojson
import json
import datetime
import math
import os
import os.path
import re
import uuid
from django.conf import settings
import cProfile

import appomatic_mapserver.maprenderers

def print_time(fn):
    def print_time(*arg, **kw):
        before = datetime.datetime.now()
        try:
            return fn(*arg, **kw)
        finally:
            after = datetime.datetime.now()
            print "TIME:", after - before
    return print_time


def profiled(filename_pattern):
    def profiled(fn):
        def profiled_fn(request, *arg, **kw):
            def profiled_fn():
                return fn(request, *arg, **kw)
            profiler = cProfile.Profile()
            try:
                return profiler.runcall(profiled_fn)
            finally:
                query = dict(request.GET.items())
                query['url'] = request.get_full_path().replace("/", "__")
                query['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                query['path'] = request.path.replace("/", "__")
                profiler.dump_stats(filename_pattern % query)

            return res
        return profiled_fn
    return profiled

#@profiled("/tmp/profile-mapserver: %(time)s %(url)s")
@fcdjangoutils.jsonview.json_view
@print_time
def mapserver(request, application):
    print "GET MAP" + repr(request.GET)
    action = request.GET.get('action', 'map')

    urlquery = dict(request.GET.iteritems())
    urlquery['application'] = application
    renderer = appomatic_mapserver.maprenderers.MapRenderer(urlquery)

    if action == 'map':
        return renderer.get_map()

    if action == 'config':
        return renderer.application.configuration

    if action == 'layers':
        return renderer.get_layer_defs()

    if action == 'timerange':
        return renderer.get_timeframe()

    if action == 'kmldir':
        directory = request.GET['directory']
        datetimemin = datetime.datetime.utcfromtimestamp(int(request.GET['datetime__gte']))
        datetimemax = datetime.datetime.utcfromtimestamp(int(request.GET['datetime__lte']))

        return {'files': ["%s/%s/doc.kml" % (directory, kmldir.strftime("%Y-%m-%d %H:%M:%S"))
                          for kmldir in (datetime.datetime.strptime(kmldir, "%Y-%m-%d %H:%M:%S")
                                         for kmldir in os.listdir(os.path.join(settings.MEDIA_ROOT, directory)))
                          if datetimemin < kmldir < datetimemax]}

def application(request, application):
    urlquery = dict(request.GET.iteritems())
    urlquery['application'] = application
    return django.shortcuts.render_to_response(
        'appomatic_mapserver/application.html',
        {'application': appomatic_mapserver.models.BaseApplication(urlquery)},
        context_instance=django.template.RequestContext(request))

def index(request):
    return django.shortcuts.render_to_response(
        'appomatic_mapserver/index.html',
        {'applications': appomatic_mapserver.models.Application.objects.all()},
        context_instance=django.template.RequestContext(request))
