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

@fcdjangoutils.jsonview.json_view
@print_time
def mapserver(request):
    print "GET MAP" + repr(request.GET)
    action = request.GET.get('action', 'map')


    if action == 'map':
        datetimemin = int(request.GET['datetime__gte'])
        datetimemax = int(request.GET['datetime__lte'])
        lon1,lat1,lon2,lat2 = [float(coord) for coord in request.GET['bbox'].split(",")]
        query = {
            "timemin": datetime.datetime.utcfromtimestamp(datetimemin),
            "timemax": datetime.datetime.utcfromtimestamp(datetimemax),
            "lonmin": min(lon1, lon2),
            "latmin": min(lat1, lat2),
            "lonmax": max(lon1, lon2),
            "latmax": max(lat1, lat2)
            }
        
        with contextlib.closing(django.db.connection.cursor()) as cur:

            bboxmin = "ST_Point(%(lonmin)s, %(latmin)s)"
            bboxmax = "ST_Point(%(lonmax)s, %(latmax)s)"
            bbox = "st_setsrid(ST_MakeBox2D(" + bboxmin + ", " + bboxmax + "), (4326))"
            bboxdiag = "ST_Distance(" + bboxmin + ", " + bboxmax + ")"

            if request.GET.get('full', 'false') == 'true':
                tolerance = None
                tolerancetest = "tolerance is null"
            else:
                cur.execute("select " + bboxdiag + " / 100", query)
                tolerance = cur.fetchone()[0]

                # Round to nearest (lower) 2^x as those are the only tolerances implemented in the view...
                # Fixme: Handle min and max...
                tolerance = 2**int(math.log(float(tolerance), 2))

                query['tolerance'] = tolerance

                tolerancetest = "tolerance = %(tolerance)s"

            sql = """
              select
                mmsi,
                ST_AsText(shape) as shape,
                timemin,
                timemax,
                name,
                type,
                length,
                url
              from
                (select
                   ais_path.mmsi,
                   ST_Intersection(
                     ST_locate_between_measures(
                       line,
                       extract(epoch from %(timemin)s::timestamp),
                       extract(epoch from %(timemax)s::timestamp)
                     ),
                     """ + bbox + """) as shape,
                   timemin,
                   timemax,
                    vessel.name,
                   vessel.type,
                   vessel.length,
                   vessel.url
                 from
                   appomatic_mapdata_aispath as ais_path
                   left outer join appomatic_mapdata_vessel as vessel on
                     ais_path.mmsi = vessel.mmsi
                 where
                   """ + tolerancetest + """
                   and not (%(timemax)s < timemin or %(timemin)s > timemax)
                   and ST_Intersects(
                     line,
                     """ + bbox + """)) as a
              where
                not ST_IsEmpty(shape)
            """
        
            cur.execute(sql, query)
            try:
                format = request.GET.get('format', 'geojson')
                if format == 'geojson':
                    features = []
                    for row in dictreader(cur):
                        geometry = shapely.wkt.loads(str(row['shape']))
                        geometry = json.loads(
                            geojson.dumps(
                                geometry))
                        del row['shape']
                        row['datetime'] = datetimemin + 1
                        feature = {"type": "Feature",
                                   "geometry": geometry,
                                   "properties": row}
                        features.append(feature)

                    return {"type": "FeatureCollection",
                            "features": features}

                elif format == 'kml':
                    kml = fastkml.kml.KML()
                    ns = '{http://www.opengis.net/kml/2.2}'
                    doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
                    kml.append(doc)

                    types = []
                    for row in dictreader(cur):
                        geometry = shapely.wkt.loads(str(row['shape']))
                        if row['mmsi']:
                            if not row['name']:
                                row['name'] = row['mmsi']
                            if not row['url']:
                                row['url'] =  "http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=" + row['mmsi']
                        placemark = fastkml.kml.Placemark(
                            ns, row['mmsi'], row['name'],
                            """<h2><a href='%(url)s'>%(name)s</a></h2><table><tr><th>MMSI</th><td>%(mmsi)s</td></tr><tr><th>Type</th><td>%(type)s</td></tr><tr><th>Length</th><td>%(length)s</td></tr></table>""" % row)

                        types.append(geometry.geom_type)
                        placemark.geometry = geometry
                        doc.append(placemark)

                    return django.http.HttpResponse(
                        kml.to_string(prettyprint=True),
                        mimetype="text/plain",
                        status=200)

            finally:
                print "TOLERANCE:", tolerance
                print "RESULTS: ", cur.rowcount


    if action == 'timerange':
        with contextlib.closing(django.db.connection.cursor()) as cur:

            cur.execute("select min(datetime), max(datetime) from ais", )
            row = cur.fetchone()

            return {'timemin': int(row[0].strftime('%s')), 'timemax': int(row[1].strftime("%s"))}

    if action == 'layers':
        return {
            'ExactEarth': {
                'type': 'MapServer.Layer.Db',
                'options': {
                    'protocol': {
                        'params': {
                            'table': 'ais_path',
                            }
                        }
                    }
                },
            'Vessel detections': {
                'type': 'MapServer.Layer.KmlDateDir',
                'options': {
                    'directory': 'vessel-detections',
                    'protocol': {
                        'params': {
                            }
                        }
                    }
                }
            }
