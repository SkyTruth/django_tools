import appomatic_pybossa_tools.models
import django.db.models
import django.db.transaction
import pytz
import httplib2
import json
import datetime
import sys

class Importer(object):
    def log(self, **info):
        self.logstatus.update(info)
        if self.out:
            self.out.write(json.dumps(self.logstatus) + "\n")
            self.out.flush()
        else:
            print info.get("status", "X")

    def __init__(self, queryset, out=None):
        self.out = out
        self.logstatus = {"done": 0}

        for appidx, app in enumerate(queryset):
            h = httplib2.Http(".cache")

            self.log(status="Getting tasks")
            resp, content = h.request(app.url + "/tasks/export?type=task&format=json", "GET")
            tasks = json.loads(content)
            for idx, taskinfo in enumerate(tasks):
                task = appomatic_pybossa_tools.models.Task.get(app, taskinfo['id'], taskinfo)

                if idx % 50 == 0:
                    django.db.transaction.commit()
                    django.db.reset_queries()
                    self.log(status=".")

            django.db.transaction.commit()
            django.db.reset_queries()

            self.log(status="Getting results")
            resp, content = h.request(app.url + "/tasks/export?type=task_run&format=json", "GET")
            results = json.loads(content)
            for idx, result in enumerate(results):
                result['created'] = datetime.datetime.strptime(result['created'], '%Y-%m-%dT%H:%M:%S.%f')
                result['finish_time'] = datetime.datetime.strptime(result['finish_time'], '%Y-%m-%dT%H:%M:%S.%f')

                task = appomatic_pybossa_tools.models.Task.get(app, result['task_id'])
                appomatic_pybossa_tools.models.Answer.get(task, result['id'], result)

                if idx % 50 == 0:
                    django.db.transaction.commit()
                    django.db.reset_queries()
                    self.log(status="*")

            django.db.transaction.commit()
            django.db.reset_queries()

            self.log(status="Computing summaries")
            dirty = appomatic_pybossa_tools.models.Task.objects.filter(dirty=True)
            for idx, task in enumerate(dirty):
                summary = {}
                def addsummary(summary, item):
                    for key, value in item.iteritems():
                        if key not in summary:
                            summary[key] = {"values": {}}
                        if isinstance(value, (list, tuple)):
                            value = dict(enumerate(value))
                        if isinstance(value, dict):
                            addsummary(summary[key], value)
                        else:
                            if value not in summary[key]["values"]:
                                summary[key]["values"][value] = 0
                            summary[key]["values"][value] += 1

                for answer in task.answers.all():
                    addsummary(summary, answer.info['info'])
                    
                def sortsummary(summary):
                    for key, values in summary.items():
                        if key == "values":
                            values = values.items()
                            values.sort(lambda a, b: cmp(a[1], b[1]), reverse=True)
                            summary[key] = values
                        else:
                            sortsummary(values)
                sortsummary(summary)
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
                    self.log(status="x")

            django.db.transaction.commit()
            django.db.reset_queries()

            self.log(done=1.0)
