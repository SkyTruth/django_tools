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
        optparse.make_option('--size',
            action='store',
            type='int',
            default=1200,
            help='The size of the task area'),
        optparse.make_option('--years',
            action='store',
            default="2005,2008,2010",
            help='Years, comma separated'),
        optparse.make_option('--region',
            action='store',
            default="US-PA",
            help='Region to filter to. Should be a value from the "code" column of the region table'),
        optparse.make_option('--format',
            action='store',
            default="pybossa",
            help='Output format: pybossa, geojson'),
        )

    layers = {"2005": {"url": "https://mapsengine.google.com/placeholder-map-2005/wms/",
                       "options": {"version": "1.3.0", "layers":"placeholder-layer-2005"}},
              "2008": {"url": "https://mapsengine.google.com/placeholder-map-2008/wms/",
                       "options": {"version": "1.3.0", "layers":"placeholder-layer-2008"}},
              "2010": {"url": "https://mapsengine.google.com/06136759344167181854-15360160187865123339-4/wms/",
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
                substring(st.code from 3) as state
              from
                appomatic_siteinfo_site s
                join appomatic_siteinfo_locationdata l on
                  s.locationdata_ptr_id = l.basemodel_ptr_id
                join appomatic_siteinfo_basemodel b on
                  l.basemodel_ptr_id = b.id
                join region r on
                  st_contains(r.the_geom, l.location)
                  and r.code = %(region)s
                join region c on
                  st_contains(c.the_geom, l.location)
                  and c.src = 'US-COUNTY'
                join region st on
                  st_contains(st.the_geom, l.location)
                  and st.src = 'US-STATE'
                join (
                  select distinct
                    se.site_id
                  from
                    appomatic_siteinfo_event e
                    join appomatic_siteinfo_siteevent se on
                      e.locationdata_ptr_id = se.event_ptr_id
                    join appomatic_siteinfo_statusevent ste on
                      se.event_ptr_id = ste.siteevent_ptr_id
                    join appomatic_siteinfo_status st on
                      ste.status_id = st.basemodel_ptr_id
                      and st.name in ('empty', 'equipment')) h on
                  s.locationdata_ptr_id = h.site_id
              order by st.name, c.name, b.guuid
            """, kwargs)

            with open(args[0], 'w') as f:

                if kwargs['format'] == 'geojson':
                    f.write('{"type": "FeatureCollection", "features": [\n')
                elif kwargs['format'] == 'pybossa':
                    f.write('[\n')

                first = True
                for site in fcdjangoutils.sqlutils.dictreader(cur):
                    for year in kwargs["years"].split(','):

                        dummy, top, dummy = geod.fwd(site['x'], site['y'], 0, kwargs['size'] / 2)
                        left, dummy, dummy = geod.fwd(site['x'], site['y'], 270, kwargs['size'] / 2)
                        right, dummy, dummy = geod.fwd(site['x'], site['y'], 90, kwargs['size'] / 2)
                        dummy, bottom, dummy = geod.fwd(site['x'], site['y'], 180, kwargs['size'] / 2)

                        info = {
                            "latitude": site['y'],
                            "longitude": site['x'],
                            "SiteID": site["guuid"],
                            "county": site["county"],
                            "state": site["state"],
                            "year": year
                            }

                        if not first:
                            f.write(",")
                        if kwargs['format'] == 'pybossa':
                            info.update(self.layers[year])
                            info.update({"bbox": "%s,%s,%s,%s" % (left, bottom, right, top)})
                            f.write(json.dumps(info) + "\n")
                        elif kwargs['format'] == 'geojson':
                            f.write(
                                geojson.dumps(
                                    geojson.Feature(
                                        geometry=geojson.Polygon(
                                            coordinates=[[[left, top], [right, top], [right, bottom], [left, bottom], [left, top]]]),
                                        properties=info
                                        )
                                    ) + "\n")

                        first = False

                if kwargs['format'] == 'geojson':
                    f.write(']}\n')
                elif kwargs['format'] == 'pybossa':
                    f.write(']\n')
