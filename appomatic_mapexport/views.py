import django.template
import django.shortcuts
import django.http
import django.db
import contextlib
import datetime
import math
import appomatic_mapexport.kmlconvert
import appomatic_mapexport.csvconvert
import appomatic_mapexport.djangorecords

def kmlformat(request):
    res = django.http.HttpResponse(
        appomatic_mapexport.kmlconvert.convert(appomatic_mapexport.djangorecords.get_records(**dict(request.GET.items())), 'extract2kml'),
        mimetype="application/vnd.google-earth.kml+xml",
        status=200)
    res['Content-Disposition'] = 'attachment; filename="export.kml"'
    return res

def csvformat(request):
    res = django.http.HttpResponse(
        appomatic_mapexport.csvconvert.convert(appomatic_mapexport.djangorecords.get_records(**dict(request.GET.items()))),
        mimetype="text/csv",
        status=200)
    res['Content-Disposition'] = 'attachment; filename="export.csv"'
    return res


def index(request):
    return django.shortcuts.render_to_response(
        'appomatic_mapexport/index.html',
        {},
        context_instance=django.template.RequestContext(request))
