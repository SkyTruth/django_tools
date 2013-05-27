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

def decodevalue(val):
    val = val.decode('latin-1')
    if val == '__None__':
        return None
    if val == '__True__':
        return True
    if val == '__False__':
        return false
    return val
    
def csvdictreader(c):
    header = [decodevalue(col) for col in c.next()]
    for row in c:
        yield dict(zip(header, (decodevalue(col) for col in row)))

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
            for idx, row in enumerate(csvdictreader(f)):

                print row['api']

                event = appomatic_siteinfo.models.FracEvent.objects.get(import_id = row['pdf_seqid'])

                event.datetime = datetime.datetime.strptime(row['fracture_date'], "%Y-%m-%d").replace(tzinfo=pytz.utc)
                event.true_vertical_depth = row['true_vertical_depth'] and float(row['true_vertical_depth'])
                event.total_water_volume = row['total_water_volume'] and float(row['total_water_volume'])
                event.published = datetime.datetime.strptime(row['published'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
                event.info.update(row)
                event.save()
                if idx % 50 == 0:
                    django.db.transaction.commit()
            django.db.transaction.commit()
