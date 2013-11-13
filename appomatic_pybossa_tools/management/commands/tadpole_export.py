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
    layers = {"2010": {"url": "https://mapsengine.google.com/06136759344167181854-15360160187865123339-4/wms/",
                       "options": {"version": "1.3.0", "layers":"06136759344167181854-16779344390631852423-4"}}}

    option_list = django.core.management.base.BaseCommand.option_list + (
        optparse.make_option('--size',
            action='store',
            type='int',
            default=200,
            help='The size of the task area'),
        optparse.make_option('--region',
            action='store',
            default="US-PA",
            help='Region to filter to. Should be a value from the "code" column of the region table'),
        optparse.make_option('--year',
            action='store',
            default="2010",
            help='Year to generate tasks for'),
        )

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
                c.latitude y, c.longitude x,
                co.name as county,
                substring(st.name from 3) as state
              from
                appomatic_mapcluster_cluster c
                join appomatic_mapcluster_report r on
                  c.report_id = r.id
                join appomatic_mapcluster_query q on
                  r.query_id = q.id
                  and q.slug='ranaarvalis-answers'
                join region reg on
                  st_contains(reg.the_geom, c.location)
                  and reg.code = %(region)s
                join region co on
                  st_contains(co.the_geom, c.location)
                  and co.src = 'US-COUNTY'
                join region st on
                  st_contains(st.the_geom, c.location)
                  and st.src = 'US-STATE'
            """, kwargs)
            for site in fcdjangoutils.sqlutils.dictreader(cur):
                info = {
                    "size": kwargs['size'],
                    "latitude": site['y'],
                    "longitude": site['x'],
                    "county": site["county"],
                    "state": site["state"],
                    "year": kwargs["year"]
                    }

                info.update(self.layers[kwargs["year"]])
                print json.dumps(info)
