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
    def handle(self, *args, **kwargs):
        try:
            return self.handle2(*args, **kwargs)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()

    @django.db.transaction.commit_on_success
    def handle2(self, *args, **kwargs):
        src = appomatic_siteinfo.models.Source.get("Permit", "")

        for row in appomatic_legacymodels.models.PaDrillingpermit.objects.filter(st_id__gt = src.import_id).order_by("st_id"):
            print "%s @ %s" %(row.complete_api_field, row.date_disposed)
            
            latitude = row.latitude_decimal
            longitude = row.longitude_decimal
            location = django.contrib.gis.geos.Point(longitude, latitude)
            
            operator = appomatic_siteinfo.models.Operator.get(row.operator)
            site = appomatic_siteinfo.models.Site.get(row.site_name, latitude, longitude)
            
            api = row.complete_api_field[:-6]
            
            well = appomatic_siteinfo.models.Well.get(api, site, latitude, longitude)
            
            info = dict((name, getattr(row, name))
                        for name in appomatic_legacymodels.models.PaDrillingpermit._meta.get_all_field_names())

            appomatic_siteinfo.models.PermitEvent(
                src = src,
                latitude = latitude,
                longitude = longitude,
                location = location,
                datetime = datetime.datetime(row.date_disposed.year, row.date_disposed.month, row.date_disposed.day).replace(tzinfo=pytz.utc),
                site = site,
                well = well,
                operator = operator,
                infourl = None,
                info = info
                ).save()
            src.import_id = row.st_id
            src.save()
