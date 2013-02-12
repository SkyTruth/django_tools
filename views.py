import django.template
import django.shortcuts
import fcdjangoutils.jsonview
import django.db
import contextlib
import datetime
import shapely.geometry
import shapely.wkb
import shapely.wkt
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

@fcdjangoutils.jsonview.json_view
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

            cur.execute("select " + bboxdiag + " / 100", query)
            tolerance = cur.fetchone()[0]

            # Round to nearest (lower) 2^x as those are the only tolerances implemented in the view...
            # Fixme: Handle min and max...
            tolerance = 2**int(math.log(float(tolerance), 2))

            query['tolerance'] = tolerance

            sql = """
              select
                mmsi,
                ST_AsText(
                  ST_Intersection(
                    ST_locate_between_measures(
                      line,
                      extract(epoch from %(timemin)s::timestamp),
                      extract(epoch from %(timemax)s::timestamp)
                    ),
                    """ + bbox + """))
              from
                ais_path
              where
                tolerance = %(tolerance)s
                and not (%(timemax)s < timemin or %(timemin)s > timemax)
                and ST_Intersects(
                  line,
                  """ + bbox + """)
            """
        
            before = datetime.datetime.now()
            cur.execute(sql, query)

            features = []
            for mmsi, shape in cur:
                #print "    ", str(shape)
                geometry = json.loads(
                    geojson.dumps(
                        shapely.wkt.loads(str(shape))))
                feature = {"type": "Feature",
                           "geometry": geometry,
                           "properties": {'datetime': datetimemin + 1}}
                features.append(feature)

            after = datetime.datetime.now()

            print "TIME:", after - before
            print "TOLERANCE:", tolerance
            print "RESULTS: ", cur.rowcount

            return {"type": "FeatureCollection",
                    "features": features}

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
                            'table': 'ais_path'
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
