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
        src = appomatic_siteinfo.models.Source.get("Spud", "")
        frack = appomatic_siteinfo.models.Operation.get("Fracking")

        for idx, row in enumerate(appomatic_legacymodels.models.PaSpud.objects.filter(st_id__gt = src.import_id).order_by("st_id")):

            print "%s @ %s" % (row.well_api_field, row.spud_date)
            
            operator = appomatic_siteinfo.models.Company.get(row.operator_s_name)

            # Format: SS-CCC-NNNNN-XX-XX
            api = row.well_api_field.split("-")
            if len(api[0]) != 2:
                api[0:0] = ['37'] # Pennsylvania is 37...
            while len(api) < 5:
                api.append('00')
            api = '-'.join(api)
            
            well = appomatic_siteinfo.models.Well.get(api, row.farm_name, row.latitude, row.longitude)
            site = well.site

            info = dict((name, getattr(row, name))
                        for name in appomatic_legacymodels.models.PaSpud._meta.get_all_field_names())

            se = appomatic_siteinfo.models.SpudEvent(
                src = src,
                latitude = row.latitude,
                longitude = row.longitude,
                datetime = datetime.datetime(row.spud_date.year, row.spud_date.month, row.spud_date.day).replace(tzinfo=pytz.utc),
                site = site,
                well = well,
                operator = operator,
                infourl = None,
                info = info
                )
            se.save()

            if row.unconventional and row.unconventional.lower() == "yes":
                se.operations.add(frack)

            src.import_id = row.st_id
            src.save()

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
        django.db.transaction.commit()
