import django.contrib.gis.db.models
import django.db.models

class Downloaded(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    src = django.db.models.CharField(max_length=128, null=False, blank=False)
    filename = django.db.models.CharField(max_length=1024, null=False, blank=False)

    class Meta:
        unique_together = ('src', 'filename',)
