import django.contrib.gis.db.models
import django.db.models
import appomatic_mapdata.models
import fcdjangoutils.fields

class TempCluster(appomatic_mapdata.models.GeographyEvent):
    objects = django.contrib.gis.db.models.GeoManager()

    buffer = appomatic_mapdata.models.GeometryField(null=True, blank=True, geography=True, db_index=True)

    reportnum = django.db.models.IntegerField()
    score = django.db.models.FloatField(null=True, blank=True)
    max_score = django.db.models.FloatField(null=True, blank=True)

class Query(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    slug = django.db.models.SlugField(null=False, blank=True)
    name = django.db.models.CharField(max_length=128, null=False, blank=False)
    description = django.db.models.TextField(null=True, blank=True)

    query = django.db.models.TextField(null=False, blank=False)
    size = django.db.models.IntegerField(null=False, blank=False)
    radius = django.db.models.FloatField(null=False, blank=False)

    #format = django.db.models.CharField(max_length=128, null=False, blank=False)
    template = django.db.models.CharField(max_length=2048, null=False, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Query, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class Report(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    query = django.db.models.ForeignKey(Query)

    timeperiod_min = django.db.models.DateTimeField()
    timeperiod_max = django.db.models.DateTimeField()


class Cluster(appomatic_mapdata.models.GeographyEvent):
    objects = django.contrib.gis.db.models.GeoManager()
    report = django.db.models.ForeignKey(Report)

    longitude_max = django.db.models.FloatField()
    longitude_avg = django.db.models.FloatField()
    longitude_stddev = django.db.models.FloatField()
    datetime_min = django.db.models.DateTimeField()
    datetime_max = django.db.models.DateTimeField()
    datetime_avg = django.db.models.DateTimeField()
    datetime_stddev = django.db.models.FloatField()
    latitude_min = django.db.models.FloatField()
    latitude_max = django.db.models.FloatField()
    latitude_avg = django.db.models.FloatField()
    latitude_stddev = django.db.models.FloatField()

    info = fcdjangoutils.fields.JsonField()
