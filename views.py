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

            cur.execute("""
              select
                count(mmsi) ,
             """ + bboxdiag + """ / 10
             from
                ais_path
              where
                ST_Intersects(
                  line,
                  """ + bbox + """)
                and not (%(timemax)s < timemin or %(timemin)s > timemax)
            """, query)
            nrresults, tolerance = cur.fetchone()

            sql = """
              select
                mmsi,
                ST_AsText(
                  ST_Intersection(
                    ST_SimplifyPreserveTopology(
                      ST_locate_between_measures(
                        line,
                        extract(epoch from %(timemin)s::timestamp),
                        extract(epoch from %(timemax)s::timestamp)
                      ),
                      """ + bboxdiag + """ / 10),
                    """ + bbox + """))
              from
                ais_path
              where
                ST_Intersects(
                  line,
                  """ + bbox + """)
                and not (%(timemax)s < timemin or %(timemin)s > timemax)
            """
        
            cur.execute(sql, query)

            features = []

            print "TOLERANCE:", tolerance
            print "RESULTS: ", nrresults
            for mmsi, shape in cur:
                #print "    ", str(shape)
                geometry = json.loads(
                    geojson.dumps(
                        shapely.wkt.loads(str(shape))))
                feature = {"type": "Feature",
                           "geometry": geometry,
                           "properties": {'datetime': datetimemin + 1}}
                features.append(feature)
            print "DONE"

            return {"type": "FeatureCollection",
                    "features": features}

    if action == 'timerange':
        with contextlib.closing(django.db.connection.cursor()) as cur:

            cur.execute("select min(datetime), max(datetime) from ais", )
            row = cur.fetchone()

            return {'timemin': int(row[0].strftime('%s')), 'timemax': int(row[1].strftime("%s"))}
