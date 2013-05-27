import django.core.management.base
import appomatic_siteinfo.models
import appomatic_renderable.models
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

    def get_source(self, tool, argument):
        sources = appomatic_renderable.models.Source.objects.filter(tool=tool, argument=argument)
        if sources:
            return sources[0]
        source = appomatic_renderable.models.Source(tool=tool, argument=argument)
        source.save()
        return source

    def handle2(self, *args, **kwargs):
        src = self.get_source("FracFocus", args[0])
        with open(args[0]) as f:
            f = iter(csv.reader(f))
            headers = f.next()
            for idx, row in enumerate(f):
                row = dict(zip(headers, row))

                print row['api']

                latitude = float(row['latitude'])
                longitude = float(row['longitude'])
                location = django.contrib.gis.geos.Point(longitude, latitude)

                operator = appomatic_siteinfo.models.Operator.get(row['operator'])
                site = appomatic_siteinfo.models.Site.get(row['well_name'], latitude, longitude)

                api = row['api']

                well = appomatic_siteinfo.models.Well.get(api, site, latitude, longitude)

                appomatic_siteinfo.models.FracEvent(
                    src = src,
                    import_id = row['seqid'],
                    latitude = latitude,
                    longitude = longitude,
                    location = location,
                    datetime = datetime.datetime.strptime(row['job_date'], "%Y-%m-%d").replace(tzinfo=pytz.utc),
                    site = site,
                    well = well,
                    operator = operator,
                    infourl = None,
                    info = row
                    ).save()
                if idx % 50 == 0:
                    django.db.transaction.commit()
            django.db.transaction.commit()
