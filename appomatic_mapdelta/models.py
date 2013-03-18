import django.contrib.gis.db.models
import django.db.models
import appomatic_mapdata.models

class Event(appomatic_mapdata.models.GeographyEvent):
    objects = django.contrib.gis.db.models.GeoManager()

    reportnum = django.db.models.IntegerField()

    min_distance = django.db.models.FloatField(null=True, blank=True)
    score = django.db.models.IntegerField(null=True, blank=True)
