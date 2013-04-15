import django.contrib.gis.db.models
import django.db.models
import appomatic_mapdata.models
import dbarray
import uuid
import django.contrib.auth.models

class Feedtag(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    name = django.db.models.CharField(max_length=1024, primary_key=True)

    class Meta:
        db_table = 'feedtag'
        managed=False

    def __unicode__(self):
        return self.name

class Feedsource(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    name = django.db.models.CharField(max_length=32)

    class Meta:
        db_table = 'FeedSource'

    def __unicode__(self):
        return self.name

class Feedentry(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    id = django.db.models.CharField(max_length=255, primary_key=True)

    title = django.db.models.CharField(max_length=255)
    link = django.db.models.CharField(max_length=255, blank=True)
    summary = django.db.models.TextField(blank=True)
    content = django.db.models.TextField(blank=True)
    lat = django.db.models.FloatField()
    lng = django.db.models.FloatField()
    source = django.db.models.ForeignKey(Feedsource, db_column="source_id")
    kml_url = django.db.models.CharField(max_length=255, blank=True)
    incident_datetime = django.db.models.DateTimeField()
    published = django.db.models.DateTimeField(blank=True, null=True)
    regions = dbarray.IntegerArrayField(null=True, blank=True) # Foreign keys to appomatic_mapdata.models.Region
    tags = dbarray.TextArrayField(null=True, blank=True)
    the_geom = django.contrib.gis.db.models.GeometryField(srid=0, blank=True, null=True)
    source_item_id = django.db.models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'feedentry'

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.source)

class RssEmailSubscription(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    id = django.db.models.CharField(primary_key=True, max_length=36, blank=True)

    confirmed = django.db.models.SmallIntegerField(default=0)

    email = django.db.models.CharField(max_length=255)
    rss_url = django.db.models.CharField(max_length=255)
    interval_hours = django.db.models.IntegerField(default=23)
    last_email_sent = django.db.models.DateTimeField(blank=True, null=True)
    last_item_updated = django.db.models.DateTimeField(blank=True, null=True)
    lat1 = django.db.models.FloatField(blank=True, null=True)
    lat2 = django.db.models.FloatField(blank=True, null=True)
    lng1 = django.db.models.FloatField(blank=True, null=True)
    lng2 = django.db.models.FloatField(blank=True, null=True)
    last_update_sent = django.db.models.DateTimeField(blank=True, null=True)
    active = django.db.models.SmallIntegerField(default=1)
    name = django.db.models.CharField(max_length=30, blank=True)

    class Meta:
        managed = False
        db_table = 'RSSEmailSubscription'

    def __unicode__(self):
        return "%s%s %s" % (self.email, [" (Disabled)", ""][not not self.active], self.rss_url)

    def save(self, *arg, **kw):
        if not self.id:
            self.id = str(uuid.uuid4())
        django.contrib.gis.db.models.Model.save(self, *arg, **kw)
