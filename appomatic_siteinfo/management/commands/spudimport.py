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

    @django.db.transaction.commit_on_success
    def handle2(self, *args, **kwargs):
        src = self.get_source("Permit", args[0])
        with open(args[0]) as f:
            f = iter(csv.reader(f))
            headers = f.next()
            for row in f:
                row = dict(zip(headers, row))

                print row['Well_API__']
                
                operator = appomatic_siteinfo.models.Operator.get(row['Operator_s_Name'])

                try:
                    latitude = float(row['Latitude'])
                    longitude = float(row['Longitude'])
                    location = django.contrib.gis.geos.Point(longitude, latitude)
                except:
                    latitude = None
                    longitude = None
                    location = None

                api = row['Well_API__'][:-6]

                well = appomatic_siteinfo.models.Well.get(api, row['Farm_Name'], latitude, longitude)
                site = well.site

                if latitude is None:
                    latitude = site.latitude
                    longitude = site.longitude
                    location = site.location

                appomatic_siteinfo.models.SpudEvent(
                    src = src,
                    latitude = latitude,
                    longitude = longitude,
                    location = location,
                    datetime = datetime.datetime.strptime(row['SPUD_Date'], "%Y-%m-%d").replace(tzinfo=pytz.utc),
                    site = site,
                    well = well,
                    operator = operator,
                    infourl = None,
                    info = row
                    ).save()
