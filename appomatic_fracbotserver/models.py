import django.db.models
import fcdjangoutils.fields
import uuid

class State(django.db.models.Model):
    siteid = django.db.models.IntegerField()
    name = django.db.models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

class County(django.db.models.Model):
    state = django.db.models.ForeignKey(State, related_name="counties")
    siteid = django.db.models.IntegerField()
    name = django.db.models.CharField(max_length=255)
    scrapepoints = django.db.models.FloatField(default=1)

    class Meta:
        unique_together = (("state", "name"),)

    def __unicode__(self):
        return "%s in %s" % (self.name, self.state)

class Client(django.db.models.Model):
    id = django.db.models.CharField(max_length=255, primary_key=True, blank=True)
    ip = django.db.models.CharField(max_length=255, blank=True)
    domain = django.db.models.CharField(max_length=512, blank=True)
    agent = django.db.models.CharField(max_length=512, blank=True)
    info = fcdjangoutils.fields.JsonField()

    def save(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        django.db.models.Model.save(self)

    def __unicode__(self):
        return self.id

class ActivityType(django.db.models.Model):
    name = django.db.models.CharField(max_length=255, unique = True)

    def __unicode__(self):
        return self.name

class Activity(django.db.models.Model):
    client = django.db.models.ForeignKey(Client, related_name="activities")
    type = django.db.models.ForeignKey(ActivityType, related_name="activities")
    datetime = django.db.models.DateTimeField(auto_now_add=True)
    info = fcdjangoutils.fields.JsonField()
    amount = django.db.models.FloatField()

    def __unicode__(self):
        return "%s by %s @ %s" % (self.type, self.client, self.datetime.strftime("%Y-%m-%d %H:%M:%S"))
