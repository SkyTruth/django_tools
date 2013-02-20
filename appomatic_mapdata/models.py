import django.contrib.gis.db.models
import django.db.models

# Hack to allow columns with no geom_type
import django.contrib.gis.db.backends.postgis.operations
def geo_db_type(self, f):
     """
     Return the database field type for the given geometry field.
     Typically this is `None` because geometry columns are added via
     the `AddGeometryColumn` stored procedure, unless the field
     has been specified to be of geography type instead.
     """
     if f.geography:
         if not self.geography:
             raise NotImplementedError('PostGIS 1.5 required for geography column support.')

         if f.srid != 4326:
             raise NotImplementedError('PostGIS 1.5 supports geography columns '
                                       'only with an SRID of 4326.')

         if f.geom_type:
             return 'geography(%s,%d)'% (f.geom_type, f.srid)
         else:
             return 'geography' # FIXME: How to handle srid?
     elif self.geometry:
         if not f.geom_type:
             return 'geometry' # FIXME: How to handle srid?

         # Postgis 2.0 supports type-based geometries.
         # TODO: Support 'M' extension.
         if f.dim == 3:
             geom_type = f.geom_type + 'Z'
         else:
             geom_type = f.geom_type
         return 'geometry(%s,%d)' % (geom_type, f.srid)
     else:
         return None
django.contrib.gis.db.backends.postgis.operations.PostGISOperations.geo_db_type = geo_db_type


class GeometryField(django.contrib.gis.db.models.GeometryField):
    geom_type = None

class Vessel(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    mmsi = django.db.models.CharField(max_length=9, null=False, blank=False, unique=True)
    name = django.db.models.CharField(max_length=128, null=True, blank=True)
    type = django.db.models.CharField(max_length=64, null=True, blank=True)
    length = django.db.models.IntegerField(null=True, blank=True)

    @property
    def url(self):
        return "http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=" + self.mmsi


class Ais(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    src = django.db.models.CharField(max_length=128, null=False, blank=False)
    mmsi = django.db.models.CharField(max_length=9, null=False, blank=False)
    datetime = django.db.models.DateTimeField(null=False, blank=False)

    latitude = django.db.models.FloatField(null=False, blank=False)
    longitude = django.db.models.FloatField(null=False, blank=False)
    true_heading = django.db.models.FloatField(null=True, blank=True)
    sog = django.db.models.FloatField(null=True, blank=True)
    cog = django.db.models.FloatField(null=True, blank=True)
    location = GeometryField(null=False, blank=False)

    vessel = django.db.models.ForeignKey(Vessel, null=True, blank=True)

    @property
    def url(self):
        return "http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=" + self.mmsi


class AisPath(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    src = django.db.models.CharField(max_length=128, null=False, blank=False)
    mmsi = django.db.models.CharField(max_length=9, null=False, blank=False)

    timemin = django.db.models.DateTimeField(null=False, blank=False)
    timemax = django.db.models.DateTimeField(null=False, blank=False)
    
    tolerance = django.db.models.FloatField(null=True, blank=True)
    line = GeometryField(null=False, blank=False)

    vessel = django.db.models.ForeignKey(Vessel, null=True, blank=True)

    @property
    def url(self):
        return "http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=" + self.mmsi
