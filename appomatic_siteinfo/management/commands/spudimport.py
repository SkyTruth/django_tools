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

        for idx, row in enumerate(appomatic_legacymodels.models.PaSpud.objects.filter(st_id__gt = src.import_id).order_by("st_id")):

            print "%s @ %s" % (row.well_api_field, row.spud_date)
            
            operator = appomatic_siteinfo.models.Company.get(row.operator_s_name)

            api = row.well_api_field[:-6]

            well = appomatic_siteinfo.models.Well.get(api, row.farm_name, row.latitude, row.longitude, conventional = (not row.unconventional) or row.unconventional.lower() != "yes")
            site = well.site

            info = dict((name, getattr(row, name))
                        for name in appomatic_legacymodels.models.PaSpud._meta.get_all_field_names())

            appomatic_siteinfo.models.SpudEvent(
                src = src,
                latitude = row.latitude,
                longitude = row.longitude,
                datetime = datetime.datetime(row.spud_date.year, row.spud_date.month, row.spud_date.day).replace(tzinfo=pytz.utc),
                site = site,
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
