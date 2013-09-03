from django.conf import settings 
import django.db.transaction
import pytz
import httplib2
import json
import appomatic_pybossa_tools.models
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

    def handle2(self, appname, *args, **kwargs):
        h = httplib2.Http(".cache")

        resp, content = h.request("http://crowdcrafting.org/app/%s/tasks/export?type=task&format=json" % appname, "GET")
        for idx, taskinfo in enumerate(json.loads(content)):
            app = appomatic_pybossa_tools.models.App.get(taskinfo['app_id'], appname)
            task = appomatic_pybossa_tools.models.Task.get(app, taskinfo['id'], taskinfo)

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
                sys.stdout.write(".")
                sys.stdout.flush()

        django.db.transaction.commit()
        django.db.reset_queries()

        resp, content = h.request("http://crowdcrafting.org/app/%s/tasks/export?type=task_run&format=json" % appname, "GET")
        for idx, result in enumerate(json.loads(content)):
            result['created'] = datetime.datetime.strptime(result['created'], '%Y-%m-%dT%H:%M:%S.%f')
            result['finish_time'] = datetime.datetime.strptime(result['finish_time'], '%Y-%m-%dT%H:%M:%S.%f')

            app = appomatic_pybossa_tools.models.App.get(result['app_id'], appname)
            task = appomatic_pybossa_tools.models.Task.get(app, result['task_id'])
            appomatic_pybossa_tools.models.Answer.get(task, result['id'], result)

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
                sys.stdout.write("*")
                sys.stdout.flush()

        django.db.transaction.commit()
        django.db.reset_queries()
        
        for idx, task in enumerate(appomatic_pybossa_tools.models.Task.objects.filter(dirty=True)):
            summary = {}
            for answer in task.answers.all():
                for key, value in answer.info['info'].iteritems():
                    if key not in summary:
                        summary[key] = {}
                    if value not in summary[key]:
                        summary[key][value] = 0
                    summary[key][value] += 1

            for key, values in summary.items():
                values = values.items()
                values.sort(lambda a, b: cmp(a[1], b[1]), reverse=True)
                summary[key] = values
            info = dict(task.info)
            info['summary'] = summary
            task.info = info
            task.dirty = False
            task.save()

            sys.stdout.write("x")
            sys.stdout.flush()

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
                sys.stdout.write("X")
                sys.stdout.flush()

        django.db.transaction.commit()
        django.db.reset_queries()
        
