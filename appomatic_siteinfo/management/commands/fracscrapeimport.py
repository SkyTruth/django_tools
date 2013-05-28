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
        src = appomatic_siteinfo.models.Source.get("FracFocus", "")

        for idx, row in enumerate(appomatic_legacymodels.models.Fracfocusscrape.objects.filter(seqid__gt = src.import_id).order_by("seqid")):

            print "%s @ %s" % (row.api, row.job_date)

            latitude = row.latitude
            longitude = row.longitude
            location = django.contrib.gis.geos.Point(longitude, latitude)

            operator = appomatic_siteinfo.models.Company.get(row.operator)
            site = appomatic_siteinfo.models.Site.get(row.well_name, latitude, longitude)

            api = row.api

            well = appomatic_siteinfo.models.Well.get(api, site, latitude, longitude)

            info = dict((name, getattr(row, name))
                        for name in appomatic_legacymodels.models.Fracfocusscrape._meta.get_all_field_names())

            appomatic_siteinfo.models.FracEvent(
                src = src,
                import_id = row.seqid,
                latitude = latitude,
                longitude = longitude,
                location = location,
                datetime = datetime.datetime(row.job_date.year, row.job_date.month, row.job_date.day).replace(tzinfo=pytz.utc),
                site = site,
                well = well,
                operator = operator,
                infourl = None,
                info = info
                ).save()
            src.import_id = row.seqid
            src.save()

            if idx % 50 == 0:
                django.db.transaction.commit()
        django.db.transaction.commit()
