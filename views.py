import django.template
import django.shortcuts
import fcdjangoutils.jsonview
import django.db
import contextlib
import datetime

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
            "datetimemin": datetime.datetime.utcfromtimestamp(datetimemin),
            "datetimemax": datetime.datetime.utcfromtimestamp(datetimemax),
            "lonmin": min(lon1, lon2),
            "latmin": min(lat1, lat2),
            "lonmax": max(lon1, lon2),
            "latmax": max(lat1, lat2)
            }
        
        with contextlib.closing(django.db.connection.cursor()) as cur:
            cur.execute("""
              select
                ais.*, vessel.*
              from
                ais
                left outer join vessel on
                  ais.mmsi = vessel.mmsi
              where
                datetime >= %(datetimemin)s
                and datetime <= %(datetimemax)s
                and longitude >= %(lonmin)s
                and longitude <= %(lonmax)s
                and latitude >= %(latmin)s
                and latitude <= %(latmax)s
              order by
                ais.mmsi, datetime limit 100""",
                        query)


            features = []

            vessel = None
            for row in dictreader(cur):
                row['datetime'] = int(row['datetime'].strftime("%s"))
                
                if vessel is None or vessel['properties']['mmsi'] != row['mmsi']:
                    if vessel is not None and len(vessel['geometry']['coordinates']) > 1:
                        features.append(vessel)
                    vessel = {'type': 'Feature', 'properties': row, 'geometry': {'type': 'LineString', 'coordinates': []}}
                vessel['geometry']['coordinates'].append([row['longitude'], row['latitude']])

                features.append({'type': 'Feature', 'properties': row, 'geometry': {'type': 'Point', 'coordinates': [row['longitude'], row['latitude']]}})


            if vessel is not None and len(vessel['geometry']['coordinates']) > 1:
                features.append(vessel)


            return {"type": "FeatureCollection",
                    "features": features}

    if action == 'timerange':
        with contextlib.closing(django.db.connection.cursor()) as cur:

            cur.execute("select min(datetime), max(datetime) from ais", )
            row = cur.fetchone()

            return {'timemin': int(row[0].strftime('%s')), 'timemax': int(row[1].strftime("%s"))}
