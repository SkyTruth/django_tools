import django.db.models
import fcdjangoutils.fields

class App(django.db.models.Model):
    appid = django.db.models.IntegerField()
    name = django.db.models.CharField(max_length=256, blank=True)
    info = fcdjangoutils.fields.JsonField(null=True, blank=True)

    @classmethod
    def get(cls, appid, name):
        apps = cls.objects.filter(appid=appid)
        if apps: return apps[0]
        app = cls(appid=appid, name=name)
        app.save()
        return app

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
