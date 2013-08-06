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

        for idx, task in enumerate(appomatic_pybossa_tools.models.Task.objects.filter(app__name="frackfinder_tadpole", id__gt = src.import_id).order_by("id")):
            # Don't use get since we have multiple sites with the same GUUID for now (!!!)
            site = appomatic_siteinfo.models.Site.objects.filter(guuid=task.info['info']['siteID'])[0]
            if 'type' not in task.info['summary']: continue

            status = appomatic_siteinfo.models.Status.get(task.info['summary']['type'][0][0])

            event = appomatic_siteinfo.models.StatusEvent(
                src = src,
                import_id = task.id,
                datetime = datetime.datetime(int(task.info['info']['year']), 1, 1).replace(tzinfo=pytz.utc),
                site = site,
                status = status,
                info = task.info
                )
            event.save()

            src.import_id = task.id
            src.save()

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()

                sys.stdout.write(".")
                sys.stdout.flush()

        django.db.transaction.commit()
