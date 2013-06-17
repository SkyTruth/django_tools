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
        src = appomatic_siteinfo.models.Source.get("Permit", "")

        for idx, row in enumerate(appomatic_legacymodels.models.PaDrillingpermit.objects.filter(st_id__gt = src.import_id).order_by("st_id")):
            print "%s @ %s" %(row.complete_api_field, row.date_disposed)
            
            operator = appomatic_siteinfo.models.Company.get(row.operator)
            
            # Format: SS-CCC-NNNNN-XX-XX
            api = row.complete_api_field.split("-")
            if len(api[0]) != 2:
                api[0:0] = ['37'] # Pennsylvania is 37...
            while len(api) < 5:
                api.append('00')
            if len(api) != 5 or len(api[0]) != 2 or len(api[1]) != 3 or len(api[2]) != 5 or len(api[3]) != 2 or len(api[4]) != 2:
                print "    Ignoring broken api: %s" % (row.complete_api_field,)
                continue
            api = '-'.join(api)
            
            well = appomatic_siteinfo.models.Well.get(api, row.site_name, row.latitude_decimal, row.longitude_decimal, conventional = (not row.unconventional) or row.unconventional.lower() != "yes")
            
            info = dict((name, getattr(row, name))
                        for name in appomatic_legacymodels.models.PaDrillingpermit._meta.get_all_field_names())

            appomatic_siteinfo.models.PermitEvent(
                src = src,
                latitude = row.latitude_decimal,
                longitude = row.longitude_decimal,
                datetime = datetime.datetime(row.date_disposed.year, row.date_disposed.month, row.date_disposed.day).replace(tzinfo=pytz.utc),
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
        django.db.transaction.commit()
