import django.db.models

class Workspace(django.db.models.Model):
    definition = django.db.models.TextField(null=False, blank=False)

class Log(django.db.models.Model):
    data = django.db.models.TextField(null=False, blank=False)
    time = django.db.models.DateTimeField(auto_now=True)
