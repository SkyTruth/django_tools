import django.contrib.gis.db.models
import fcdjangoutils.fields
import uuid

class State(django.contrib.gis.db.models.Model):
    siteid = django.db.models.IntegerField()
    name = django.db.models.CharField(max_length=256, unique=True)

    def __unicode__(self):
        return self.name

class County(django.contrib.gis.db.models.Model):
    state = django.db.models.ForeignKey(State, related_name="counties")
    siteid = django.db.models.IntegerField()
    name = django.db.models.CharField(max_length=256)
    scrapepoints = django.db.models.FloatField(default=1)

    class Meta:
        unique_together = (("state", "name"),)

    def __unicode__(self):
        return "%s in %s" % (self.name, self.state)

class Client(django.contrib.gis.db.models.Model):
    id = django.db.models.CharField(max_length=256, primary_key=True, blank=True)
    ip = django.db.models.CharField(max_length=256)
    domain = django.db.models.CharField(max_length=512)
    agent = django.db.models.CharField(max_length=512)
    info = fcdjangoutils.fields.JsonField()

    def save(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        django.contrib.gis.db.models.Model.save(self)

    def __unicode__(self):
        return self.id

class ActivityType(django.contrib.gis.db.models.Model):
    name = django.db.models.CharField(max_length=256, unique = True)

    def __unicode__(self):
        return self.name

class Activity(django.contrib.gis.db.models.Model):
    client = django.db.models.ForeignKey(Client, related_name="activities")
    type = django.db.models.ForeignKey(ActivityType, related_name="activities")
    datetime = django.db.models.DateTimeField(auto_now_add=True)
    info = fcdjangoutils.fields.JsonField()
    amount = django.db.models.FloatField()

    def __unicode__(self):
        return "%s by %s @ %s" % (self.type, self.client, self.datetime.strftime("%Y-%m-%d %H:%M:%S"))
