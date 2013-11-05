import optparse
import fcdjangoutils.sqlutils
import json
import geojson
import contextlib
import pyproj
import shapely.wkt
import shapely.geometry
import shapely.affinity
import django.core.management.base
import django.db.transaction
import django.db
from django.conf import settings 

geod = pyproj.Geod(ellps="WGS84")

class Command(django.core.management.base.BaseCommand):

    option_list = django.core.management.base.BaseCommand.option_list + (
        optparse.make_option('--year',
            action='store',
            default="2010",
            help='Region to filter to. Should be a value from the "code" column of the region table'),
        optparse.make_option('--region',
            action='store',
            default="US-PA",
            help='Region to filter to. Should be a value from the "code" column of the region table'),
        optparse.make_option('--format',
            action='store',
            default="pybossa",
            help='Output format: pybossa, geojson'),
        )

    layers = {"2010": {"url": "https://mapsengine.google.com/06136759344167181854-15360160187865123339-4/wms/",
                       "options": {"version": "1.3.0", "layers":"06136759344167181854-16779344390631852423-4"}}}

    @django.db.transaction.commit_manually
    def handle(self, *args, **kwargs):
        try:
            return self.handle2(*args, **kwargs)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()

    def handle2(self, *args, **kwargs):
        with contextlib.closing(django.db.connection.cursor()) as cur:
            cur.execute("""
              select
                l.latitude y,
                l.longitude x,
                b.guuid as guuid,
                c.name as county,
                substring(st.code from 4) as state
              from
                appomatic_siteinfo_site s
                join appomatic_siteinfo_locationdata l on
                  s.locationdata_ptr_id = l.basemodel_ptr_id
                join appomatic_siteinfo_basemodel b on
                  l.basemodel_ptr_id = b.id
                join region c on
                  st_contains(c.the_geom, l.location)
                  and c.src = 'US-COUNTY'
                join region st on
                  st_contains(st.the_geom, l.location)
                  and st.src = 'US-STATE'
                join sitesforranaarvalis ra on
                  b.guuid = ra.siteid
            """, kwargs)

            if kwargs['format'] == 'geojson':
                print '{"type": "FeatureCollection", "features": ['

            first = True
            for site in fcdjangoutils.sqlutils.dictreader(cur):

                dummy, top, dummy = geod.fwd(site['x'], site['y'], 0, 600)
                left, dummy, dummy = geod.fwd(site['x'], site['y'], 270, 600)
                right, dummy, dummy = geod.fwd(site['x'], site['y'], 90, 600)
                dummy, bottom, dummy = geod.fwd(site['x'], site['y'], 180, 600)
                
                info = {
                    "latitude": site['y'],
                    "longitude": site['x'],
                    "SiteID": site["guuid"],
                    "county": site["county"],
                    "state": site["state"],
                    "year": kwargs["year"]
                    }

                if kwargs['format'] == 'pybossa':
                    info.update(self.layers[kwargs["year"]])
                    info.update({"bbox": "%s,%s,%s,%s" % (left, bottom, right, top)})
                    print json.dumps(info)
                elif kwargs['format'] == 'geojson':
                    if not first:
                        print ","
                    print geojson.dumps(
                        geojson.Feature(
                            geometry=geojson.Polygon(
                                coordinates=[[[left, top], [right, top], [right, bottom], [left, bottom], [left, top]]]),
                            properties=info
                            )
                        )
                    
                first = False

            if kwargs['format'] == 'geojson':
                print ']}'
