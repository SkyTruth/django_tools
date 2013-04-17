import django.contrib.gis.db.models
import django.db.models
import dbarray

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

class ImportedData(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    src = django.db.models.CharField(max_length=128, null=False, blank=False, db_index=True)
    srcfile = django.db.models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class Vessel(ImportedData):
    objects = django.contrib.gis.db.models.GeoManager()

    mmsi = django.db.models.CharField(max_length=16, null=False, blank=False, unique=True) # max_length *should* be 9, but we do get some odd data...
    name = django.db.models.CharField(max_length=128, null=True, blank=True)
    type = django.db.models.CharField(max_length=64, null=True, blank=True)
    length = django.db.models.IntegerField(null=True, blank=True)

    @property
    def url(self):
        return "http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=" + self.mmsi

class Region(ImportedData):
    class Meta:
        db_table = 'region'

    name = django.db.models.CharField(max_length=50, null=False, blank=False, db_index=True)
    code = django.db.models.CharField(max_length=20, null=False, blank=False, db_index=True)
    the_geom = GeometryField(null=True, blank=True)
    simple_geom = GeometryField(null=True, blank=True)
    kml = django.db.models.TextField(null=True, blank=True)

class Event(ImportedData):
    objects = django.contrib.gis.db.models.GeoManager()
    datetime = django.db.models.DateTimeField(null=False, blank=False, db_index=True)

    latitude = django.db.models.FloatField(null=False, blank=False, db_index=True)
    longitude = django.db.models.FloatField(null=False, blank=False, db_index=True)
    location = GeometryField(null=False, blank=False, db_index=True)

    region = dbarray.IntegerArrayField(null=True, blank=True) # Really a set of foreign keys to Region

    quality = django.db.models.FloatField(default = 1.0, db_index=True)

    class Meta:
        abstract = True

class Path(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    src = django.db.models.CharField(max_length=128, null=False, blank=False)
    srcfile = django.db.models.CharField(max_length=1024, null=True, blank=True)

    timemin = django.db.models.DateTimeField(null=False, blank=False)
    timemax = django.db.models.DateTimeField(null=False, blank=False)
    
    tolerance = django.db.models.FloatField(null=True, blank=True)
    line = GeometryField(null=False, blank=False)

    region = dbarray.IntegerArrayField(null=True, blank=True) # Really a set of foreign keys to Region

    class Meta:
        abstract = True


class Ais(Event):
    objects = django.contrib.gis.db.models.GeoManager()
    mmsi = django.db.models.CharField(max_length=16, null=False, blank=False)

    true_heading = django.db.models.FloatField(null=True, blank=True)
    sog = django.db.models.FloatField(null=True, blank=True)
    cog = django.db.models.FloatField(null=True, blank=True)

    vessel = django.db.models.ForeignKey(Vessel, null=True, blank=True)

    URL_PATTERN = "http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=%(mmsi)s"
    URL_PATTERN_ITU = "http://www.itu.int/cgi-bin/htsh/mars/ship_search.sh?sh_mmsi=%(mmsi)s"

    @property
    def url(self):
        return self.URL_PATTERN % {'mmsi': self.mmsi}


class AisPath(Path):
    objects = django.contrib.gis.db.models.GeoManager()

    mmsi = django.db.models.CharField(max_length=16, null=False, blank=False)
    vessel = django.db.models.ForeignKey(Vessel, null=True, blank=True)

    @property
    def url(self):
        return Ais.URL_PATTERN % {'mmsi': self.mmsi}

class Sar(Event):
    name = django.db.models.CharField(max_length=128, null=False, blank=False)

    duration = django.db.models.IntegerField(null=True, blank=True)
    BeamMode = django.db.models.CharField(max_length=8, null=False, blank=False)
    Polarizations = django.db.models.CharField(max_length=8, null=False, blank=False)
    ProductType = django.db.models.CharField(max_length=8, null=False, blank=False)
    ImageID = django.db.models.IntegerField(null=True, blank=True)
    Counter = django.db.models.IntegerField(null=True, blank=True)
    ProcessessingID = django.db.models.IntegerField(null=True, blank=True)
    Customer = django.db.models.CharField(max_length=16, null=False, blank=False)
    FileType = django.db.models.CharField(max_length=16, null=False, blank=False)

    Probability = django.db.models.IntegerField(null=True, blank=True)
    DetectionId = django.db.models.CharField(max_length=128, null=False, blank=False)
    ProductStartTime = django.db.models.DateTimeField(null=True, blank=True)
    ProductStopTime = django.db.models.DateTimeField(null=True, blank=True)
    Beam = django.db.models.FloatField(null=True, blank=True)
    Length = django.db.models.FloatField(null=True, blank=True)
    Type = django.db.models.CharField(max_length=128, null=False, blank=False)
    Heading = django.db.models.FloatField(null=True, blank=True)
    ProductId = django.db.models.CharField(max_length=128, null=False, blank=False)


class GeographyEvent(Event):
    glocation = GeometryField(null=False, blank=False, geography=True, db_index=True)

    class Meta:
        abstract = True

class Viirs(Event):
    name = django.db.models.CharField(max_length=128, null=False, blank=False)

    RadiantOutput = django.db.models.FloatField(null=True, blank=True, db_index=True)
    Temperature = django.db.models.FloatField(null=True, blank=True, db_index=True)
    RadiativeHeat = django.db.models.FloatField(null=True, blank=True, db_index=True)
    footprint = django.db.models.FloatField(null=True, blank=True, db_index=True)
    SatZenithAngle = django.db.models.FloatField(null=True, blank=True)
    SourceID = django.db.models.CharField(max_length=128, null=False, blank=False, db_index=True)
