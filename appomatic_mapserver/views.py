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
from django.conf import settings


def index(request):
    return django.shortcuts.render_to_response(
        'appomatic_mapserver/index.html',
        {},
        context_instance=django.template.RequestContext(request))

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


class MapRenderer(object):
    implementations = {}

    def __new__(cls, request, *arg, **kw):
        if cls is MapRenderer:
            type = request.GET.get('format', 'appomatic_mapserver.views.MapRendererGeojson')
            return cls.implementations[type](request, *arg, **kw)
        else:
            return object.__new__(cls, request, *arg, **kw)

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            if name != "MapRenderer":
                MapRenderer.implementations[members.get('__module__', '__main__') + "." + name] = cls

    def __init__(self, request):
        self.request = request

    def __enter__(self):
        self.map = MapSource(self.request).__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.map.__exit__(type, value, traceback)


    def get_row_template(self):
        return "<h2><a href='%(url)s'>%(name)s</a></h2><table><tr><th>MMSI</th><td>%(mmsi)s</td></tr><tr><th>Type</th><td>%(type)s</td></tr><tr><th>Length</th><td>%(length)s</td></tr></table>"


class MapRendererGeojson(MapRenderer):
    def get_map(self):
        query = self.map.get_query()

        features = []
        for row in self.map.get_map_data():
            geometry = shapely.wkt.loads(str(row['shape']))
            geometry = fcdjangoutils.jsonview.from_json(
                geojson.dumps(
                    geometry))
            del row['shape']
            row['datetime'] = query['timeminstamp'] + 1
            feature = {"type": "Feature",
                       "geometry": geometry,
                       "properties": row}
            features.append(feature)

        return django.http.HttpResponse(
            fcdjangoutils.jsonview.to_json(
                {"type": "FeatureCollection",
                 "features": features}),
            mimetype="application/json",
            status=200)

class MapRendererKml(MapRenderer):
    def get_map(self):
        query = self.map.get_query()

        kml = fastkml.kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
        kml.append(doc)

        types = []
        for row in self.map.get_map_data():
            geometry = shapely.wkt.loads(str(row['shape']))
            placemark = fastkml.kml.Placemark(
                ns, row['name'], row['name'],
                self.get_row_template() % row)

            types.append(geometry.geom_type)
            placemark.geometry = geometry
            doc.append(placemark)

        return django.http.HttpResponse(
            kml.to_string(prettyprint=True),
            mimetype="application/vnd.google-earth.kml+xml",
            status=200)


class MapSource(object):
    implementations = {}

    def __new__(cls, request, *arg, **kw):
        if cls is MapSource:
            type = request.GET.get('type', 'tolerance_path')
            return cls.implementations[type](request, *arg, **kw)
        else:
            return object.__new__(cls, request, *arg, **kw)

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            if name != "MapSource":
                MapSource.implementations[members.get('__module__', '__main__') + "." + name] = cls

    def __init__(self, request):
        self.request = request

    def __enter__(self):
        self.cur = django.db.connection.cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.cur.close()

    def get_query(self):
        datetimemin = int(self.request.GET['datetime__gte'])
        datetimemax = int(self.request.GET['datetime__lte'])
        lon1,lat1,lon2,lat2 = [float(coord) for coord in self.request.GET['bbox'].split(",")]
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
        table = self.request.GET["table"]
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

        if self.request.GET.get('full', 'false') == 'true':
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


    if action == 'map':
        with MapRenderer(request) as map:
            return map.get_map()

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
        return {
            'ExactEarth': {
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
            'Sar': {
                'type': 'MapServer.Layer.Db',
                'options': {
                    'protocol': {
                        'params': {
                            'type': 'appomatic_mapserver.views.EventMap',
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
