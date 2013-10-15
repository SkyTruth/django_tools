import django.contrib.gis.db.models
import django.db.models
import appomatic_mapdata.models

class Cluster(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    reportnum = django.db.models.IntegerField()
    incident_datetime = django.db.models.DateTimeField()

    incidenttype = django.db.models.CharField(max_length=20)

    location = appomatic_mapdata.models.GeometryField(null=False, blank=False, db_index=True)
    buffer = appomatic_mapdata.models.GeometryField(null=True, blank=True, db_index=True)

    score = django.db.models.FloatField(null=True, blank=True)
    max_score = django.db.models.FloatField(null=True, blank=True)


class NrcReport(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    reportnum = django.db.models.IntegerField()
    incident_datetime = django.db.models.DateTimeField()

    incidenttype = django.db.models.CharField(max_length=20)

    lat = django.db.models.FloatField()
    lng = django.db.models.FloatField()

    location = appomatic_mapdata.models.GeometryField(null=False, blank=False, db_index=True)

    geocode_source = django.db.models.CharField(max_length=20)
