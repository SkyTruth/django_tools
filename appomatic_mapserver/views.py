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
        self.template = MapTemplate(urlquery)
        self.source = MapSource(urlquery)

class MapTemplate(object):
    implementations = {}

    def __new__(cls, urlquery, *arg, **kw):
        if cls is MapTemplate:
            type = urlquery.get('template', 'appomatic_mapserver.views.MapTemplateSimple')
            print "XXXXXX", urlquery, type

            return cls.implementations[type](urlquery, *arg, **kw)
        else:
            return object.__new__(cls, *arg, **kw)

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

class MapTemplateSar(MapTemplateSimple):
    def row_kml_style(self, row):
        id = row.get('id', row.get('name', row.get('mmsi', str(uuid.uuid4()))))
        style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s" % id)
        style.append_style(fastkml.styles.IconStyle(
            '{http://www.opengis.net/kml/2.2}',
            "style-item-%s-icon" % id,
            icon_href = "http://alerts.skytruth.org/markers/red-x.png"
            ))
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
        self.template = MapTemplate(self.urlquery)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def get_layers(self):
        if 'type' in self.urlquery and 'table' in self.urlquery:
            yield MapLayer(self.urlquery)
        else:
            for name, layer in self.get_layer_defs().iteritems():
                urlquery = dict(self.urlquery)
                urlquery.update(layer['options']['protocol']['params'])
                urlquery['name'] = name
                yield MapLayer(urlquery)

    def get_layer_defs(self):
        return {
            'ExactEarthPath': {
                'type': 'MapServer.Layer.Db',
                'options': {
                    'protocol': {
                        'params': {
                            'type': 'appomatic_mapserver.views.TolerancePathMap',
                            'table': 'appomatic_mapdata_aispath',
                            }
                        }
                    }
                },
            'ExactEarthMarkers': {
                'type': 'MapServer.Layer.Db',
                'options': {
                    'protocol': {
                        'params': {
                            'type': 'appomatic_mapserver.views.EventMap',
                            'table': 'appomatic_mapdata_ais',
                            }
                        }
                    }
                },
            'Sar': {
                'type': 'MapServer.Layer.Db',
                'options': {
                    'protocol': {
                        'params': {
                            'type': 'appomatic_mapserver.views.EventMap',
                            'template': 'appomatic_mapserver.views.MapTemplateSar',
                            'table': 'appomatic_mapdata_sar',
                            }
                        }
                    }
                },
            # 'Vessel detections': {
            #     'type': 'MapServer.Layer.KmlDir',
            #     'options': {
            #         'protocol': {
            #             'params': {
            #                 'directory': 'vessel-detections',
            #                 }
            #             }
            #         }
            #     }
            }


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

    def __new__(cls, urlquery, *arg, **kw):
        if cls is MapSource:
            type = urlquery.get('type', 'tolerance_path')
            return cls.implementations[type](urlquery, *arg, **kw)
        else:
            return object.__new__(cls, urlquery, *arg, **kw)

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            if name != "MapSource":
                MapSource.implementations[members.get('__module__', '__main__') + "." + name] = cls

    def __init__(self, urlquery):
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
        table = self.urlquery["table"]
        if not re.search("^[a-z_]*$", table):
            raise Exception("SQL injections are so not cool. Try again.")
        return table

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
            """ + self.get_table() + """
          where
            not (%(timemax)s < datetime or %(timemin)s > datetime)
            and ST_Contains(
              """ + bboxsql['bbox'] + """, location)
        """

        self.cur.execute(sql, query)
        try:
            for row in dictreader(self.cur):
                yield row
        finally:
            print "RESULTS: ", self.cur.rowcount


@fcdjangoutils.jsonview.json_view
@print_time
def mapserver(request):
    print "GET MAP" + repr(request.GET)
    action = request.GET.get('action', 'map')

    renderer = MapRenderer(dict(request.GET.iteritems()))

    if action == 'map':
        return renderer.get_map()

    if action == 'timerange':
        with contextlib.closing(django.db.connection.cursor()) as cur:

            cur.execute("select min(timemin), max(timemax) from appomatic_mapdata_aispath", )
            row = cur.fetchone()

            return {'timemin': int(row[0].strftime('%s')), 'timemax': int(row[1].strftime("%s"))}

    if action == 'kmldir':
        directory = request.GET['directory']
        datetimemin = datetime.datetime.utcfromtimestamp(int(request.GET['datetime__gte']))
        datetimemax = datetime.datetime.utcfromtimestamp(int(request.GET['datetime__lte']))

        return {'files': ["%s/%s/doc.kml" % (directory, kmldir.strftime("%Y-%m-%d %H:%M:%S"))
                          for kmldir in (datetime.datetime.strptime(kmldir, "%Y-%m-%d %H:%M:%S")
                                         for kmldir in os.listdir(os.path.join(settings.MEDIA_ROOT, directory)))
                          if datetimemin < kmldir < datetimemax]}

    if action == 'layers':
        return renderer.get_layer_defs()


def index(request):
    return django.shortcuts.render_to_response(
        'appomatic_mapserver/index.html',
        {},
        context_instance=django.template.RequestContext(request))
