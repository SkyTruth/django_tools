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
        src = appomatic_siteinfo.models.Source.get("FracFocus", "Report")

        for idx, row in enumerate(appomatic_legacymodels.models.Fracfocusreport.objects.filter(seqid__gt = src.import_id).order_by("seqid")):

            print row.api

            event = appomatic_siteinfo.models.FracEvent.objects.get(import_id = row.pdf_seqid)

            event.datetime = datetime.datetime(row.fracture_date.year, row.fracture_date.month, row.fracture_date.day).replace(tzinfo=pytz.utc)
            event.true_vertical_depth = row.true_vertical_depth
            event.total_water_volume = row.total_water_volume
            event.published = row.published.replace(tzinfo=pytz.utc)
            event.info.update(dict((name, getattr(row, name))
                                   for name in appomatic_legacymodels.models.Fracfocusreport._meta.get_all_field_names()))
            event.save()

            src.import_id = row.seqid
            src.save()

            if idx % 50 == 0:
                django.db.transaction.commit()
        django.db.transaction.commit()
