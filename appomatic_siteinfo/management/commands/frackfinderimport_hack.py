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
import pytz
import csv

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
        src = appomatic_siteinfo.models.Source.get("Frackfinder", "")

        with open(args[0]) as f:
            for idx, row in enumerate(csv.DictReader(f)):
                # Cols: longitude,latitude,siteID,year,county,url,class,class-source,class-quality

                site = appomatic_siteinfo.models.Site.objects.get(guuid=row['siteID'])
                timestamp = datetime.datetime(int(row['year']), 1, 1).replace(tzinfo=pytz.utc)
                status = appomatic_siteinfo.models.Status.get({
                        "NO PAD": "nopad",
                        "PAD": "empty",
                        "PAD-EQUIP": "equipment",
                        "unknown": "unknown"
                        }[row['class']])

                existing = appomatic_siteinfo.models.StatusEvent.objects.filter(site=site, datetime=timestamp)
                if existing:
                    if existing[0].status.name != status.name:
                        existing[0].status = status
                        existing[0].save()
                        sys.stdout.write("+"); sys.stdout.flush()
                    else:
                        sys.stdout.write("-"); sys.stdout.flush()
                else:
                    event = appomatic_siteinfo.models.StatusEvent(
                        src = src,
                        import_id = None,
                        datetime = timestamp,
                        site = site,
                        status = status,
                        )
                    event.save()
                    sys.stdout.write("*"); sys.stdout.flush()

                if idx % 50 == 49:
                    django.db.transaction.commit()
                    django.db.reset_queries()

                    sys.stdout.write("X"); sys.stdout.flush()

            django.db.transaction.commit()
