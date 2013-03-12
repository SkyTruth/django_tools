import django.contrib.gis.db.models
import django.db.models
import appomatic_mapdata.models

class Cluster(appomatic_mapdata.models.GeographyEvent):
    objects = django.contrib.gis.db.models.GeoManager()

    buffer = appomatic_mapdata.models.GeometryField(null=True, blank=True, geography=True, db_index=True)

    reportnum = django.db.models.IntegerField()
    score = django.db.models.FloatField(null=True, blank=True)
    max_score = django.db.models.FloatField(null=True, blank=True)
