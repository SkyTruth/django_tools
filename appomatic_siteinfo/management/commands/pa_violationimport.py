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
        src = appomatic_siteinfo.models.Source.get("Violation", "")

        for idx, row in enumerate(appomatic_legacymodels.models.PaViolation.objects.filter(st_id__gt = src.import_id).order_by("st_id")):
            if row.permit_api is None:
                print "IGNORING %s @ %s (missing API)" %(row.st_id, row.inspectiondate)
                continue

            # Format: SS-CCC-NNNNN-XX-XX
            api = row.permit_api.split("-")
            if len(api[0]) != 2:
                api[0:0] = ['37'] # Pennsylvania is 37...
            while len(api) < 5:
                api.append('00')
            if len(api) != 5 or len(api[0]) != 2 or len(api[1]) != 3 or len(api[2]) != 5 or len(api[3]) != 2 or len(api[4]) != 2:
                print "    Ignoring broken api: %s" % (row.permit_api,)
                continue
            api = '-'.join(api)
            
            print "%s @ %s" %(api, row.inspectiondate)
            
            operator = appomatic_siteinfo.models.Company.get(row.operator)
            
            well = appomatic_siteinfo.models.Well.get(api)
            
            info = dict((name, getattr(row, name))
                        for name in appomatic_legacymodels.models.PaViolation._meta.get_all_field_names())

            appomatic_siteinfo.models.ViolationEvent(
                src = src,
                latitude = well.latitude,
                longitude = well.longitude,
                location = well.location,
                datetime = datetime.datetime(row.inspectiondate.year, row.inspectiondate.month, row.inspectiondate.day).replace(tzinfo=pytz.utc),
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
