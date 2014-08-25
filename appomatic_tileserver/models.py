import django.db.models

class Workspace(django.db.models.Model):
    definition = django.db.models.TextField(null=False, blank=False)

    def __str__(self):
        return "Workspace %s" % self.id

class Log(django.db.models.Model):
    data = django.db.models.TextField(null=False, blank=False)
    time = django.db.models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s: %s" % (self.time, self.data)
