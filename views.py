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
                   ST_AsText(
                     ST_Intersection(
                       ST_locate_between_measures(
                         line,
                         extract(epoch from %(timemin)s::timestamp),
                         extract(epoch from %(timemax)s::timestamp)
                       ),
                       """ + bbox + """)) as shape,
                   timemin,
                   timemax,
                   vessel.name,
                   vessel.type,
                   vessel.length,
                   vessel.url
                 from
                   ais_path
                   left outer join vessel on
                     ais_path.mmsi = vessel.mmsi
                 where
                   tolerance = %(tolerance)s
                   and not (%(timemax)s < timemin or %(timemin)s > timemax)
                   and ST_Intersects(
                     line,
                     """ + bbox + """)) as a
              where
                not ST_IsEmpty(shape)
            """
        
            before = datetime.datetime.now()
            cur.execute(sql, query)


            format = request.GET.get('format', 'geojson')

            if format == 'geojson':
                features = []
                for row in dictreader(cur):
                    #print "    ", str(row['shape'])
                    geometry = json.loads(
                        geojson.dumps(
                            shapely.wkt.loads(str(row['shape']))))
                    del row['shape']
                    row['datetime'] = datetimemin + 1
                    feature = {"type": "Feature",
                               "geometry": geometry,
                               "properties": row}
                    features.append(feature)

                after = datetime.datetime.now()

                print "TIME:", after - before
                print "TOLERANCE:", tolerance
                print "RESULTS: ", cur.rowcount

                return {"type": "FeatureCollection",
                        "features": features}

            elif format == 'kml':

                # def kmlify(rows):
                #     kml = fastkml.kml.KML()
                #     ns = '{http://www.opengis.net/kml/2.2}'
                #     doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
                #     kml.append(doc)

                #     for row in rows:
                #         if row['mmsi']:
                #             if not row['name']:
                #                 row['name'] = row['mmsi']
                #             if not row['url']:
                #                 row['url'] =  "http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=" + row['mmsi']
                #         placemark = fastkml.kml.Placemark(
                #             ns, row['mmsi'], row['name'],
                #             """<h2><a href='%(url)s'>%(name)s</a></h2><table><tr><th>MMSI</th><td>%(mmsi)s</td></tr><tr><th>Type</th><td>%(type)s</td></tr><tr><th>Length</th><td>%(length)s</td></tr></table>""" % row)
                #         geom = shapely.wkt.loads(str(row['shape']))
                #         placemark.geometry = geom
                #         doc.append(placemark)

                #     return kml.to_string(prettyprint=True)

                # rows = list(dictreader(cur))

                # import pdb
                # pdb.set_trace()




                kml = fastkml.kml.KML()
                ns = '{http://www.opengis.net/kml/2.2}'
                doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
                kml.append(doc)

                types = []
                for row in dictreader(cur):
                    if row['mmsi']:
                        if not row['name']:
                            row['name'] = row['mmsi']
                        if not row['url']:
                            row['url'] =  "http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=" + row['mmsi']
                    placemark = fastkml.kml.Placemark(
                        ns, row['mmsi'], row['name'],
                        """<h2><a href='%(url)s'>%(name)s</a></h2><table><tr><th>MMSI</th><td>%(mmsi)s</td></tr><tr><th>Type</th><td>%(type)s</td></tr><tr><th>Length</th><td>%(length)s</td></tr></table>""" % row)
                    geom = shapely.wkt.loads(str(row['shape']))

                    types.append(geom.geom_type)
                    placemark.geometry = geom
                    doc.append(placemark)

                return django.http.HttpResponse(
                    kml.to_string(prettyprint=True),
                    mimetype="text/plain",
                    status=200)


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
