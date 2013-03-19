import django.contrib.gis.db.models
import django.db.models
import appomatic_mapdata.models
import dbarray

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
