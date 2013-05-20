import django.contrib.gis.db.models
import django.db.models
import django.core.urlresolvers
import django.forms
import django.contrib.gis.geos
import django.contrib.gis.measure
import django.contrib.auth.models
import ckeditor.fields
import fcdjangoutils.geomodels
import appomatic_renderable.models
import appomatic_mapserver.maptemplates
import appomatic_mapserver.models
import datetime
from django.conf import settings
import pytz


# Some basic abstract classes

class BaseModel(django.contrib.gis.db.models.Model, appomatic_renderable.models.Renderable):
    objects = django.contrib.gis.db.models.GeoManager()
    
    src = django.db.models.ForeignKey(appomatic_renderable.models.Source, blank=True, null=True)
    quality = django.db.models.FloatField(default = 1.0, db_index=True)

    def get_absolute_url(self):
        return django.core.urlresolvers.reverse('appomatic_siteinfo.views.basemodel', kwargs={'id': self.id})
    

class LocationData(BaseModel):
    objects = django.contrib.gis.db.models.GeoManager()
    latitude = django.db.models.FloatField(null=True, blank=True, db_index=True)
    longitude = django.db.models.FloatField(null=True, blank=True, db_index=True)
    location = django.contrib.gis.db.models.GeometryField(null=True, blank=True, db_index=True)
    
    def set_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        if latitude is not None and longitude is not None:
            self.location = django.contrib.gis.geos.Point(longitude, latitude)
        else:
            self.location = None

    def update_location(self, latitude, longitude):
        if latitude is not None and longitude is not None and (self.latitude is None or self.longitude is None):
            self.set_location(latitude, longitude)
            self.save()


# Concrete classes

class Operator(BaseModel):
    name = django.db.models.CharField(max_length=256, null=False, blank=False, db_index=True)

    @classmethod
    def get(cls, name):
        aliases = OperatorAlias.objects.filter(name=name)
        if aliases:
            return aliases[0].operator
        operator = Operator(name = name)
        operator.save()
        alias = OperatorAlias(operator = operator, name = name)
        alias.save()
        return operator

    def __unicode__(self):
        return self.name

class OperatorAlias(BaseModel):
    name = django.db.models.CharField(max_length=256, null=False, blank=False, db_index=True)
    operator = django.db.models.ForeignKey(Operator, related_name="aliases")

    def __unicode__(self):
        return "%s: %s" % (self.operator.name, self.name)

class Site(LocationData):
    objects = django.contrib.gis.db.models.GeoManager()

    name = django.db.models.CharField(max_length=256, null=False, blank=False, db_index=True)
    datetime = django.db.models.DateTimeField(null=True, blank=True, db_index=True)

    operators = django.db.models.ManyToManyField(Operator, related_name='sites')

    @classmethod
    def get(cls, name, latitude, longitude):
        aliases = SiteAlias.objects.filter(name=name)
        if aliases:
            site = aliases[0].site
        else:
            if longitude is not None and latitude is not None:
                location = django.contrib.gis.geos.Point(longitude, latitude)
                sites = cls.objects.filter(location__distance_lt=(location, django.contrib.gis.measure.Distance(m=300)))
            else:
                sites = []
            if sites:
                site = sites[0]
            else:
                site = Site(name = name)
                site.save()
            alias = SiteAlias(site = site, name = name)
            alias.save()

        site.update_location(latitude, longitude)
        return site

    def __unicode__(self):
        return self.name

    def handle__read(self, request, style):
        return {'comment_form': CommentForm()}

    def handle__comment(self, request, style):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.site = self
            if request.user.is_authenticated():
                comment.author = request.user
            comment.save()
            form = CommentForm()
        return {'comment_form': form}

class SiteAlias(BaseModel):
    name = django.db.models.CharField(max_length=256, null=False, blank=False, db_index=True)
    site = django.db.models.ForeignKey(Site, related_name="aliases")

    def __unicode__(self):
        return "%s: %s" % (self.site, self.name)

class Well(LocationData):
    objects = django.contrib.gis.db.models.GeoManager()

    api = django.db.models.CharField(max_length=128, null=False, blank=False, db_index=True)
    site = django.db.models.ForeignKey(Site, related_name="wells")
    datetime = django.db.models.DateTimeField(null=True, blank=True, db_index=True)

    operators = django.db.models.ManyToManyField(Operator, related_name='wells')

    def update_location(self, latitude, longitude):
        LocationData.update_location(self, latitude, longitude)
        self.site.update_location(latitude, longitude)

    @classmethod
    def get(cls, api, site_name, latitude, longitude):
        wells = cls.objects.filter(api=api)
        if wells:
            well = wells[0]
        else:
            site = Site.get(site_name, latitude, longitude)
            well = Well(
                api=api,
                site=site)
            well.save()
        well.update_location(latitude, longitude)
        return well

    def __unicode__(self):
        return "%s: %s" % (self.site, self.api)

    def handle__read(self, request, style):
        return {'comment_form': CommentForm()}

    def handle__comment(self, request, style):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.site = self.site
            comment.well = self
            if request.user.is_authenticated():
                comment.author = request.user
            comment.save()
            form = CommentForm()
        return {'comment_form': form}


# Event types

class Event(LocationData):
    objects = django.contrib.gis.db.models.GeoManager()

    datetime = django.db.models.DateTimeField(null=False, blank=False, db_index=True, default=lambda:datetime.datetime.now(pytz.utc))

    def __unicode__(self):
        return "%s" % (self.datetime,)

    class Meta:
        ordering = ('-datetime', )

class SiteEvent(Event):
    objects = django.contrib.gis.db.models.GeoManager()

    site = django.db.models.ForeignKey(Site, related_name="events")
    well = django.db.models.ForeignKey(Well, blank=True, null=True, related_name="events")

    def save(self, *arg, **kw):
        Event.save(self, *arg, **kw)
        if not self.site.datetime or self.site.datetime < self.datetime:
            self.site.datetime = self.datetime
            self.site.save()
        if self.well and (not self.well.datetime or self.well.datetime < self.datetime):
            self.well.datetime = self.datetime
            self.well.save()

    def __unicode__(self):
        return "%s @ %s" % (self.datetime, self.well or self.site)

class OperatorEvent(SiteEvent):
    objects = django.contrib.gis.db.models.GeoManager()

    operator = django.db.models.ForeignKey(Operator, related_name="events")

    def save(self, *arg, **kw):
        SiteEvent.save(self, *arg, **kw)
        self.operator.sites.add(self.site)
        if self.well:
            self.operator.wells.add(self.well)

    def __unicode__(self):
        return "%s @ %s for %s" % (self.datetime, self.well or self.site, self.operator)


class OperatorInfoEvent(OperatorEvent):
    objects = django.contrib.gis.db.models.GeoManager()

    infourl = django.db.models.TextField(null=True, blank=True)
    info = fcdjangoutils.fields.JsonField(null=True, blank=True)

class PermitEvent(OperatorInfoEvent):
    objects = django.contrib.gis.db.models.GeoManager()

class SpudEvent(OperatorInfoEvent):
    objects = django.contrib.gis.db.models.GeoManager()

class UserEvent(SiteEvent):
    objects = django.contrib.gis.db.models.GeoManager()

    author = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="events", blank=True, null=True)

    def __unicode__(self):
        return "%s @ %s for %s" % (self.datetime, self.well or self.site, self.author)

class CommentEvent(UserEvent):
    objects = django.contrib.gis.db.models.GeoManager()

    content = ckeditor.fields.RichTextField(verbose_name="Comment", config_name='small')




class CommentForm(django.forms.ModelForm):
    class Meta:
        model = CommentEvent
        fields = ['content']


# Map stuff

class SiteInfoMap(appomatic_mapserver.models.BuiltinApplication):
    name = 'SiteInfo'
    configuration = {
        "center": {
            "lat": 40.903133814657984,
            "lon": -79.1784667968776},
        "timemax": "end",
        "zoom": 8,
        "classes": "noeventlist",
        "timemin": "start",
        "options": {
            "protocol": {
                "params": {
                    "limit": 50
                    }
                }
            }
        }


    def get_layer(self, urlquery):
        return SiteInfoLayer(self)

    def get_layers(self):
        return [SiteInfoLayer(self)]

class SiteInfoLayer(appomatic_mapserver.models.BuiltinLayer):
    name="Sites"

    backend_type = "appomatic_mapserver.mapsources.EventMap"
    template = "appomatic_siteinfo.models.MapTemplate"

    definition = {
        "classes": "noeventlist",
        "options": {
            "protocol": {
                "params": {
                    "limit": 50
                    }
                }
            }
        }

    @property
    def query(self):
        # Maybe compile using the right sql compiler here?
        return "(%s)" % (Event.objects.all().query,)

class MapTemplate(appomatic_mapserver.maptemplates.MapTemplateSimple):
    name = "SiteInfo site"
    
    def row_generate_text(self, row):
        row['url'] = django.core.urlresolvers.reverse('appomatic_siteinfo.views.basemodel', kwargs={'id': row['id']})
        row['target'] = 'objinfo'
        appomatic_mapserver.maptemplates.MapTemplateSimple.row_generate_text(self, row)
        del row['description']

        row['style'] = {
          "graphicName": "circle",
          "fillOpacity": 1.0,
          "fillColor": "#0000ff",
          "strokeOpacity": 1.0,
          "strokeColor": "#ff0000",
          "strokeWidth": 1,
          "pointRadius": 6,
          }
