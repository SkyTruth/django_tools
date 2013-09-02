import django.core.management.base
import appomatic_siteinfo.models
import appomatic_pybossa_tools.models
import optparse
import contextlib
import datetime
import sys
import os.path
import logging
from django.conf import settings 
import django.db.transaction
import django.db
import contextlib
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
        with contextlib.closing(django.db.connection.cursor()) as cur:
            cur.execute("alter table appomatic_siteinfo_well add column info text;")

        for idx, x in enumerate(appomatic_siteinfo.models.Site.objects.all()):
            for y in x.wells.all():
                y.info = x.info
                y.save()

            sys.stdout.write(".")
            sys.stdout.flush()

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
                sys.stdout.write("*")
                sys.stdout.flush()

        django.db.transaction.commit()
        django.db.reset_queries()

        sys.stdout.write("\nMERGING\n")
        sys.stdout.flush()

        for idx, x in enumerate(appomatic_siteinfo.models.Site.objects.all()):
            if x.info.get('conventional', False):
                x = x.merge()
                info = dict(x.info)
                del info['conventional']
                x.info = info
                x.save()

            sys.stdout.write(".")
            sys.stdout.flush()

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
                sys.stdout.write("*")
                sys.stdout.flush()

        django.db.transaction.commit()
        django.db.reset_queries()
