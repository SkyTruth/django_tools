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
        total = appomatic_siteinfo.models.BaseModel.objects.all().count()
        for idx, row in enumerate(appomatic_siteinfo.models.BaseModel.objects.all()):
            row.save()

            if idx % 50 == 0:
                print "%.2f%%" % (100 * idx / float(total))
                django.db.transaction.commit()
                django.db.reset_queries()
        django.db.transaction.commit()
