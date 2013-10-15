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
        frack = appomatic_siteinfo.models.Operation.get("Fracking")
        total = appomatic_siteinfo.models.Event.objects.filter().count()
	print "TOTAL:", total
        for idx, e in enumerate(appomatic_siteinfo.models.Event.objects.all()):
            isfrack = (   (e.src.tool == "WVPermit" and e.info.get('permit_type', None) in ('HORIW', 'HRW6A'))
                       or (e.src.tool == "Permit" and str(e.info.get('unconventional', '')).lower() == "yes")
                       or e.src.tool == "FracFocus")
            if isfrack:
                e.leafclassobject.operations.add(frack)

            sys.stdout.write(".")
            sys.stdout.flush()

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
                sys.stdout.write("\n%s%%\n" % (float(idx) / total * 100))
                sys.stdout.flush()

        django.db.transaction.commit()
        django.db.reset_queries()
