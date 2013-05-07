import django.contrib.gis.db.models
import django.db.models
import datetime

class Downloaded(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    src = django.db.models.CharField(max_length=128, null=False, blank=False)
    filename = django.db.models.CharField(max_length=1024, null=False, blank=False)
    datetime = django.db.models.DateTimeField(blank=True, null=True)

    parent = django.db.models.ForeignKey("Downloaded", blank=True, null=True, related_name="children")

    class Meta:
        unique_together = ('src', 'parent', 'filename',)

    def save(self, *args, **kwargs):
        if not self.datetime:
            self.datetime = datetime.datetime.today()
        super(Downloaded, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s:%s//%s @ %s" % (self.src, self.parent_id, self.filename, self.datetime)

class Proxy(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    last_usage = django.db.models.DateTimeField(blank=True, null=True)
    last_update = django.db.models.DateTimeField(blank=True, null=True)
    type = django.db.models.CharField(max_length=128, null=False, blank=False)
    country = django.db.models.CharField(max_length=128, null=False, blank=False)
    anonymity = django.db.models.CharField(max_length=128, null=False, blank=False)

    ip_address = django.db.models.CharField(max_length=16, null=False, blank=False)
    port = django.db.models.IntegerField(null=False, blank=False)

    class Meta:
        unique_together = ('ip_address', 'port')

    @classmethod
    def get(cls):
        res = cls.objects.filter(type='HTTP', last_update__gte = datetime.datetime.now() - datetime.timedelta(0.5)).order_by('last_usage')[0]
        res.last_usage = datetime.datetime.now()
        res.save()
        return res

    def __unicode__(self):
        return "%s://%s:%s" % (self.type, self.ip_address, self.port)
