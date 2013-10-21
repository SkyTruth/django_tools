import fcdjangoutils.sqlutils
import json
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
                latitude y, longitude x
              from
                appomatic_siteinfo_site s
                join appomatic_siteinfo_locationdata l on
                  s.locationdata_ptr_id = l.basemodel_ptr_id
                join appomatic_siteinfo_basemodel b on
                  l.basemodel_ptr_id = b.id
                join region r on
                  st_contains(r.the_geom, l.location)
                  and r.name = 'Tioga County, PA'
                join (
                  select distinct
                    se.site_id
                  from
                    appomatic_siteinfo_event e
                    join appomatic_siteinfo_siteevent se on
                      e.locationdata_ptr_id = se.event_ptr_id
                      and e.datetime < '2011-01-01'
                    join appomatic_siteinfo_statusevent ste on
                      se.event_ptr_id = ste.siteevent_ptr_id
                    join appomatic_siteinfo_status st on
                      ste.status_id = st.basemodel_ptr_id
                      and st.name in ('empty', 'equipment')) h on
                  s.locationdata_ptr_id = h.site_id
            """)

            for site in fcdjangoutils.sqlutils.dictreader(cur):

                dummy, top, dummy = geod.fwd(site['x'], site['y'], 0, 750)
                left, dummy, dummy = geod.fwd(site['x'], site['y'], 270, 750)
                right, dummy, dummy = geod.fwd(site['x'], site['y'], 90, 750)
                dummy, bottom, dummy = geod.fwd(site['x'], site['y'], 180, 750)
                
                print json.dumps({
                        "url": "https://mapsengine.google.com/06136759344167181854-15360160187865123339-4/wms/",
                        "options": {"version": "1.3.0", "layers":"06136759344167181854-16779344390631852423-4"},
                        "bbox": "%s,%s,%s,%s" % (left, bottom, right, top)
                        })
