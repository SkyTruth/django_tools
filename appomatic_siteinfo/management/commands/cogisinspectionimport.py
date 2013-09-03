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

nad83 = pyproj.Proj(init="EPSG:4269")
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
        src = appomatic_siteinfo.models.Source.get("CogisInspection", "")

        for idx, row in enumerate(appomatic_legacymodels.models.Cogisinspection.objects.filter(st_id__gt = src.import_id).order_by("st_id")):
            print "%s @ %s" %(row.insp_api_num, row.date)
            
            operator = appomatic_siteinfo.models.Company.get(row.operator)
            
            # Format: SS-CCC-NNNNN-XX-XX
            api = row.insp_api_num.split("-")
            if len(api[0]) != 2:
                api[0:0] = ['47'] # West Virginia is 47...
            while len(api) < 5:
                api.append('00')
            if len(api) != 5 or len(api[0]) != 2 or len(api[1]) != 3 or len(api[2]) != 5 or len(api[3]) != 2 or len(api[4]) != 2:
                print "    Ignoring broken api: %s" % (row.insp_api_num,)
                continue
            api = '-'.join(api)

            try:
                lon, lat = pyproj.transform(nad83, wgs84, row.site_lng, row.site_lat)
            except:
                lon = lat = None

            well = appomatic_siteinfo.models.Well.get(api, None, lat, lon)
            
            info = dict((name, getattr(row, name))
                        for name in appomatic_legacymodels.models.Cogisinspection._meta.get_all_field_names())

            appomatic_siteinfo.models.InspectionEvent(
                src = src,
                import_id = row.st_id,
                latitude = lat,
                longitude = lon,
                datetime = datetime.datetime(row.date.year, row.date.month, row.date.day).replace(tzinfo=pytz.utc),
                site = well.site,
                well = well,
                operator = operator,
                infourl = None,
                info = info
                ).save()
            src.import_id = row.st_id
            src.save()

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
        django.db.transaction.commit()
