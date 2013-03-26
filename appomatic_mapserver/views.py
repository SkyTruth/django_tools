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
import appomatic_mapdata.models
import os
import os.path
import re
import uuid
import appomatic_mapserver.models
from django.conf import settings


def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))

def print_time(fn):
    def print_time(*arg, **kw):
        before = datetime.datetime.now()
        try:
            return fn(*arg, **kw)
        finally:
            after = datetime.datetime.now()
            print "TIME:", after - before
    return print_time

class MapLayer(object):
    def __init__(self, urlquery):
        self.urlquery = urlquery
        self.layerdef = appomatic_mapserver.models.Layer.objects.get(slug=self.urlquery['layer'], application__slug=self.urlquery['application'])
        self.template = MapTemplate(self, urlquery)
        self.source = MapSource(self, urlquery)

class MapTemplate(object):
    implementations = {}

    def __new__(cls, layer, urlquery, *arg, **kw):
        if cls is MapTemplate:
            return cls.implementations[layer.layerdef.template](layer, urlquery, *arg, **kw)
        else:
            return object.__new__(cls, layer, urlquery, *arg, **kw)

    def __init__(self, layer, urlquery, *arg, **kw):
        self.layer = layer
        self.urlquery = urlquery

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            if name != "MapTemplate":
                MapTemplate.implementations[members.get('__module__', '__main__') + "." + name] = cls

class MapTemplateSimple(MapTemplate):
    def row_name(self, row):
        return ""

    def row_description(self, row):
        header = "<h2>%(name)s</h2>"
        if "url" in row:
            header = "<h2><a href='%(url)s'>%(name)s</a></h2>"
        cols = [col for col in row.keys() if col not in ("shape", "location")]
        cols.sort()
        template = header + '<table>%s</table>' % ''.join("<tr><th>%s</th><td>%%(%s)s</td></tr>" % (col, col) for col in cols)
        return template % row

    def group_name(self, row):
        return "%(name)s" % row

    def group_description(self, row):
        return ""
    
    def row_kml_style(self, row):
        id = row.get('id', row.get('name', row.get('mmsi', str(uuid.uuid4()))))
        style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s" % id)
        style.append_style(fastkml.styles.IconStyle(
            '{http://www.opengis.net/kml/2.2}',
            "style-item-%s-icon" % id,
            icon_href = "http://alerts.skytruth.org/markers/red-x.png"
            ))
        return style

class MapTemplateCog(MapTemplateSimple):
    def row_kml_style(self, row):
        id = row.get('id', row.get('name', row.get('mmsi', str(uuid.uuid4()))))
        try:
            c = min(float(row['sog']), 15) * 17
        except:
            c = 0
        color = 'ff00%02x%02x' % (c, 255-c)
        style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s" % id)
        style.append_style( fastkml.styles.IconStyle(
            '{http://www.opengis.net/kml/2.2}',
            "style-item-%s-icon" % id,
            icon_href = "http://alerts.skytruth.org/markers/vessel_direction.png",
            #  <hotSpot x="16" y="3" xunits="pixels" yunits="pixels"/>
            heading = row.get('cog', 0),
            color = color))
        return style

class MapRenderer(object):
    implementations = {}

    def __new__(cls, urlquery, *arg, **kw):
        if cls is MapRenderer:
            type = urlquery.get('format', 'appomatic_mapserver.views.MapRendererGeojson')
            return cls.implementations[type](urlquery, *arg, **kw)
        else:
            return object.__new__(cls, urlquery, *arg, **kw)

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            if name != "MapRenderer":
                MapRenderer.implementations[members.get('__module__', '__main__') + "." + name] = cls

    def __init__(self, urlquery):
        self.urlquery = urlquery
        self.application = appomatic_mapserver.models.Application.objects.get(slug=self.urlquery['application'])

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def get_layers(self):
        if 'layer' in self.urlquery:
            yield MapLayer(self.urlquery)
        else:
            for name, layer in self.get_layer_defs().iteritems():
                urlquery = dict(self.urlquery)
                urlquery.update(layer['options']['protocol']['params'])
                urlquery['name'] = name
                yield MapLayer(urlquery)

    def get_timeframe(self):
        timeframe = {'timemin': None, 'timemax':None}
        for layer in self.get_layers():
            with layer.source as source:
                new = source.get_timeframe()
                if timeframe['timemin'] is None or timeframe['timemin'] > new['timemin']:
                    timeframe['timemin'] = new['timemin']
                if timeframe['timemax'] is None or timeframe['timemax'] < new['timemax']:
                    timeframe['timemax'] = new['timemax']
        return timeframe

    def get_layer_defs(self):
        return self.application.layer_defs


class MapRendererGeojson(MapRenderer):
    def get_map(self):
        features = []

        for layer in self.get_layers():
            with layer.source as source:
                for row in source.get_map_data():
                    geometry = shapely.wkt.loads(str(row['shape']))
                    geometry = fcdjangoutils.jsonview.from_json(
                        geojson.dumps(
                            geometry))
                    del row['shape']
                    feature = {"type": "Feature",
                               "geometry": geometry,
                               "properties": row}
                    features.append(feature)

        res = django.http.HttpResponse(
            fcdjangoutils.jsonview.to_json(
                {"type": "FeatureCollection",
                 "features": features}),
            mimetype="application/json",
            status=200)
        res['Content-disposition'] = 'attachment; filename=export.geojson'
        return res

class MapRendererKml(MapRenderer):
    def get_map(self):
        kml = fastkml.kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
        kml.append(doc)

        for layer in self.get_layers():
            folder = fastkml.kml.Folder(ns, "group-%s" % layer.urlquery.get('name', str(uuid.uuid4())))
            doc.append(folder)

            with layer.source as source:
                for row in source.get_map_data():
                    geometry = shapely.wkt.loads(str(row['shape']))
                    placemark = fastkml.kml.Placemark(
                        ns, row['name'],
                        layer.template.row_name(row),
                        layer.template.row_description(row))
                    placemark.append_style(layer.template.row_kml_style(row))
                    placemark.geometry = geometry
                    folder.append(placemark)

        res = django.http.HttpResponse(
            kml.to_string(prettyprint=True),
            mimetype="application/vnd.google-earth.kml+xml",
            status=200)
        res['Content-disposition'] = 'attachment; filename=export.kml'
        return res


class MapSource(object):
    implementations = {}

    def __new__(cls, layer, urlquery, *arg, **kw):
        if cls is MapSource:
            return cls.implementations[layer.layerdef.backend_type](layer, urlquery, *arg, **kw)
        else:
            return object.__new__(cls, layer, urlquery, *arg, **kw)

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            if name != "MapSource":
                MapSource.implementations[members.get('__module__', '__main__') + "." + name] = cls

    def __init__(self, layer, urlquery):
        self.layer = layer
        self.urlquery = urlquery

    def __enter__(self):
        self.cur = django.db.connection.cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.cur.close()

    def get_query(self):
        datetimemin = int(self.urlquery['datetime__gte'])
        datetimemax = int(self.urlquery['datetime__lte'])
        lon1,lat1,lon2,lat2 = [float(coord) for coord in self.urlquery['bbox'].split(",")]
        return {
            "timeminstamp": datetimemin,
            "timemaxstamp": datetimemax,
            "timemin": datetime.datetime.utcfromtimestamp(datetimemin),
            "timemax": datetime.datetime.utcfromtimestamp(datetimemax),
            "lonmin": min(lon1, lon2),
            "latmin": min(lat1, lat2),
            "lonmax": max(lon1, lon2),
            "latmax": max(lat1, lat2)
            }

    def get_table(self):
        return self.layer.layerdef.query

    def get_bboxsql(self):
        bboxmin = "ST_Point(%(lonmin)s, %(latmin)s)"
        bboxmax = "ST_Point(%(lonmax)s, %(latmax)s)"
        bbox = "st_setsrid(ST_MakeBox2D(" + bboxmin + ", " + bboxmax + "), (4326))"
        bboxdiag = "ST_Distance(" + bboxmin + ", " + bboxmax + ")"
        return {
            "bboxmin": bboxmin,
            "bboxmax": bboxmax,
            "bbox": bbox,
            "bboxdiag": bboxdiag
            }

    def get_map_data(self):
        for row in self.get_map_data_raw():
            if row.get('mmsi', None):
                if not row.get('name', None):
                    row['name'] = row['mmsi']
                if not row.get('url', None):
                    row['url'] = appomatic_mapdata.models.Ais.URL_PATTERN % row

                row['itu_url'] = appomatic_mapdata.models.Ais.URL_PATTERN_ITU % row

            if not row.get('mmsi', None):
                row['mmsi'] = ''
            if not row.get('name', None):
                row['name'] = ''
            if not row.get('url', None):
                row['url'] = ''
            if not row.get('type', None):
                row['type'] = ''
            if not row.get('length', None):
                row['length'] = ''


            yield row

class TolerancePathMap(MapSource):
    def get_tolerance(self):
        query = self.get_query()
        bboxsql = self.get_bboxsql()

        if self.urlquery.get('full', 'false') == 'true':
            return None
        else:
            self.cur.execute("select " + bboxsql['bboxdiag'] + " / 100", query)
            tolerance = self.cur.fetchone()[0]

            # Round to nearest (lower) 2^x as those are the only tolerances implemented in the view...
            # Fixme: Handle min and max...
            return 2**int(math.log(float(tolerance), 2))

    def get_map_data_raw(self):
        query = self.get_query()
        bboxsql = self.get_bboxsql()

        query['tolerance'] = self.get_tolerance()

        tolerancetest = "tolerance = %(tolerance)s"
        if query['tolerance'] is None:
            tolerancetest = "tolerance is null"

        sql = """
          select
            mmsi,
            ST_AsText(shape) as shape,
            extract(epoch from timemin) as datetime,
            timemin,
            timemax,
            name,
            type,
            length
          from
            (select
               ais_path.mmsi,
               ST_Intersection(
                 ST_locate_between_measures(
                   line,
                   extract(epoch from %(timemin)s::timestamp),
                   extract(epoch from %(timemax)s::timestamp)
                 ),
                 """ + bboxsql['bbox'] + """) as shape,
               timemin,
               timemax,
                vessel.name,
               vessel.type,
               vessel.length
             from
               """ + self.get_table() + """ as ais_path
               left outer join appomatic_mapdata_vessel as vessel on
                 ais_path.mmsi = vessel.mmsi
             where
               """ + tolerancetest + """
               and not (%(timemax)s < timemin or %(timemin)s > timemax)
               and ST_Intersects(
                 line,
                 """ + bboxsql['bbox'] + """)) as a
          where
            not ST_IsEmpty(shape)
        """

        self.cur.execute(sql, query)
        try:
            for row in dictreader(self.cur):
                yield row
        finally:
            print "TOLERANCE:", query['tolerance']
            print "RESULTS: ", self.cur.rowcount


    def get_timeframe(self):
        self.cur.execute("select min(timemin), max(timemax) from " + self.get_table() + " as a")
        row = self.cur.fetchone()
        return {'timemin': int(row[0].strftime('%s')), 'timemax': int(row[1].strftime("%s"))}


class EventMap(MapSource):
    def get_map_data_raw(self):
        query = self.get_query()
        bboxsql = self.get_bboxsql()

        sql = """
          select
            *,
            extract(epoch from datetime) as datetime,
            ST_AsText(location) as shape
          from
            """ + self.get_table() + """ as a
          where
            not (%(timemax)s < datetime or %(timemin)s > datetime)
            and ST_Contains(
              """ + bboxsql['bbox'] + """, location)
          order by
            a.datetime desc
        """

        if 'limit' in self.urlquery:
            sql += "limit %(limit)s"
            query['limit'] = self.urlquery['limit']

        self.cur.execute(sql, query)
        try:
            for row in dictreader(self.cur):
                yield row
        finally:
            print "RESULTS: ", self.cur.rowcount

    def get_timeframe(self):
        self.cur.execute("select min(datetime), max(datetime) from " + self.get_table() + " as a")
        row = self.cur.fetchone()
        return {'timemin': int(row[0].strftime('%s')), 'timemax': int(row[1].strftime("%s"))}


@fcdjangoutils.jsonview.json_view
@print_time
def mapserver(request, application):
    print "GET MAP" + repr(request.GET)
    action = request.GET.get('action', 'map')

    urlquery = dict(request.GET.iteritems())
    urlquery['application'] = application
    renderer = MapRenderer(urlquery)

    if action == 'map':
        return renderer.get_map()

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
    return django.shortcuts.render_to_response(
        'appomatic_mapserver/application.html',
        {'application': appomatic_mapserver.models.Application.objects.get(slug=application)},
        context_instance=django.template.RequestContext(request))

def index(request):
    return django.shortcuts.render_to_response(
        'appomatic_mapserver/index.html',
        {'applications': appomatic_mapserver.models.Application.objects.all()},
        context_instance=django.template.RequestContext(request))
