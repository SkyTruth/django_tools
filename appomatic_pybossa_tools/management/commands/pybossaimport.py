from django.conf import settings 
import django.db.transaction
import pytz
import httplib2
import json
import appomatic_pybossa_tools.models
import appomatic_pybossa_tools.importer
import datetime
import sys

def dictreader(rows):
    rows = iter(rows)
    header = rows.next()
    for row in rows:
        yield dict(zip(header, row))

class Command(django.core.management.base.BaseCommand):

    @django.db.transaction.commit_manually
    def handle(self, *args, **kwargs):
        try:
            return self.handle2(*args, **kwargs)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()

    def handle2(self, servername, appname, *args, **kwargs):
        appomatic_pybossa_tools.importer.Importer(appomatic_pybossa_tools.models.App.objects.filter(server__name=servername, name=appname))
