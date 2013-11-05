import django.db.models
import fcdjangoutils.fields
import django.db.transaction
import pytz
import httplib2
import json
import datetime
import sys

class Server(django.db.models.Model):
    name = django.db.models.CharField(max_length=256, blank=True)
    url = django.db.models.CharField(max_length=1024, blank=True)
    info = fcdjangoutils.fields.JsonField(null=True, blank=True)

    def __unicode__(self):
        return self.name

class App(django.db.models.Model):
    server = django.db.models.ForeignKey(Server, related_name="apps")
    name = django.db.models.CharField(max_length=256)
    info = fcdjangoutils.fields.JsonField(null=True, blank=True)

    @property
    def url(self):
        return "%s/app/%s" % (self.server.url, self.name)

    def __unicode__(self):
        return "%s @ %s" % (self.name, self.server.name)


class Task(django.db.models.Model):
    app = django.db.models.ForeignKey(App, related_name="tasks")
    taskid = django.db.models.IntegerField()
    info = fcdjangoutils.fields.JsonField(null=True, blank=True)
    dirty = django.db.models.BooleanField(blank=True, default=True)

    @classmethod
    def get(cls, app, taskid, info = None):
        tasks = cls.objects.filter(app=app, taskid=taskid)
        if tasks:
            task = tasks[0]
            if info is not None:
                task.info = info
                task.save()
            return task
        task = cls(app=app, taskid=taskid, info=info)
        task.save()
        return task

    def __unicode__(self):
        name = self.taskid
        if self.info:
            for key, value in self.info.iteritems():
                key = key.lower()
                if 'site' in key or 'name' in key:
                    name = value
                    break
        return "%s in %s" % (name, self.app)

class Answer(django.db.models.Model):
    task = django.db.models.ForeignKey(Task, related_name="answers")
    answerid = django.db.models.IntegerField()
    info = fcdjangoutils.fields.JsonField(null=True, blank=True)

    @classmethod
    def get(cls, task, answerid, info = None):
        answers = cls.objects.filter(task=task, answerid=answerid)
        if answers:
            answer = answers[0]
            if info is not None:
                answer.info = info
                answer.save()
            return answer
        answer = cls(task=task, answerid=answerid, info=info)
        answer.save()
        return answer

    def save(self):
        django.db.models.Model.save(self)
        if not self.task.dirty:
            self.task.dirty = True
            self.task.save()

    def __unicode__(self):
        return "%s for %s" % (self.answerid, self.task)
