import django.core.management.base
import appomatic_siteinfo.models
import appomatic_legacymodels.models
import optparse
import contextlib
import datetime
import sys
import os.path
import logging
import csv
import django.contrib.gis.geos
from django.conf import settings 
import django.db.transaction
import pytz
import pyproj

datums = {
#    1: pyproj.Proj(init="EPSG:26917"),
#    84: pyproj.Proj(init="EPSG:26917"),
    27: pyproj.Proj(init="EPSG:26717"), # NAD 27 UTM 17N
    83: pyproj.Proj(init="EPSG:26917")  # NAD 83 UTM 17N
    }
wgs84 = pyproj.Proj(init="EPSG:4326")

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
        src = appomatic_siteinfo.models.Source.get("WVPermit", "")

        for idx, row in enumerate(appomatic_legacymodels.models.WvDrillingpermit.objects.filter(st_id__gt = src.import_id).order_by("st_id")):
            print "%s @ %s" %(row.api, row.permit_activity_date)
            
            operator = appomatic_siteinfo.models.Company.get(row.current_operator)
            
            # Format: SS-CCC-NNNNN-XX-XX
            api = row.api.split("-")
            if len(api[0]) != 2:
                api[0:0] = ['47'] # West Virginia is 47...
            while len(api) < 5:
                api.append('00')
            if len(api) != 5 or len(api[0]) != 2 or len(api[1]) != 3 or len(api[2]) != 5 or len(api[3]) != 2 or len(api[4]) != 2:
                print "    Ignoring broken api: %s" % (row.api,)
                continue
            api = '-'.join(api)
            
            try:
                lon, lat = pyproj.transform(datums[row.datum], wgs84, row.utm_east, row.utm_north)
            except:
                print "IGN"
                continue

            well = appomatic_siteinfo.models.Well.get(api, row.farm_name, lat, lon)
            
            info = dict((name, getattr(row, name))
                        for name in appomatic_legacymodels.models.WvDrillingpermit._meta.get_all_field_names())

            appomatic_siteinfo.models.PermitEvent(
                src = src,
                latitude = lat,
                longitude = lon,
                datetime = datetime.datetime(row.permit_activity_date.year, row.permit_activity_date.month, row.permit_activity_date.day).replace(tzinfo=pytz.utc),
                site = well.site,
                well = well,
                operator = operator,
                infourl = None,
                info = info,
                import_id = row.st_id,
                ).save()
            src.import_id = row.st_id
            src.save()

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
        django.db.transaction.commit()
