import django.contrib.gis.db.models
import django.db.models
import django.core.urlresolvers
import fcdjangoutils.geomodels
import appomatic_renderable.models
import django.contrib.auth.models
import ckeditor.fields
import django.contrib.gis.geos
import django.contrib.gis.measure
import appomatic_mapserver.maptemplates
import django.forms
import datetime
from django.conf import settings
import pytz


# Some basic abstract classes

class ImportedData(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    
    src = django.db.models.ForeignKey(appomatic_renderable.models.Source, blank=True, null=True)
    quality = django.db.models.FloatField(default = 1.0, db_index=True)

    class Meta:
        abstract = True


class LocationData(django.contrib.gis.db.models.Model):
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

    class Meta:
        abstract = True




# Concrete classes

class Operator(ImportedData, appomatic_renderable.models.Renderable):
    name = django.db.models.CharField(max_length=256, null=False, blank=False, db_index=True)

    def get_absolute_url(self):
        return django.core.urlresolvers.reverse('appomatic_siteinfo.views.operator', kwargs={'id': self.id})
    
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

class OperatorAlias(ImportedData):
    name = django.db.models.CharField(max_length=256, null=False, blank=False, db_index=True)
    operator = django.db.models.ForeignKey(Operator, related_name="aliases")

    def __unicode__(self):
        return "%s: %s" % (self.operator.name, self.name)

class Site(ImportedData, LocationData, appomatic_renderable.models.Renderable):
    name = django.db.models.CharField(max_length=256, null=False, blank=False, db_index=True)
    datetime = django.db.models.DateTimeField(null=True, blank=True, db_index=True)

    def get_absolute_url(self):
        return django.core.urlresolvers.reverse('appomatic_siteinfo.views.site', kwargs={'id': self.id})

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

    def handle_read(self, request, style):
        return {'comment_form': CommentForm()}

    def handle_comment(self, request, style):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.site = self
            if request.user.is_authenticated():
                comment.author = request.user
            comment.save()
            form = CommentForm()
        return {'comment_form': form}

class SiteAlias(ImportedData):
    name = django.db.models.CharField(max_length=256, null=False, blank=False, db_index=True)
    site = django.db.models.ForeignKey(Site, related_name="aliases")

    def __unicode__(self):
        return "%s: %s" % (self.site, self.name)

class Well(ImportedData, LocationData, appomatic_renderable.models.Renderable):
    api = django.db.models.CharField(max_length=128, null=False, blank=False, db_index=True)
    site = django.db.models.ForeignKey(Site, related_name="wells")
    datetime = django.db.models.DateTimeField(null=True, blank=True, db_index=True)

    def get_absolute_url(self):
        return django.core.urlresolvers.reverse('appomatic_siteinfo.views.well', kwargs={'id': self.id})

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

    def handle_read(self, request, style):
        return {'comment_form': CommentForm()}

    def handle_comment(self, request, style):
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

class Event(ImportedData, LocationData, appomatic_renderable.models.Renderable):
    objects = django.contrib.gis.db.models.GeoManager()
    datetime = django.db.models.DateTimeField(null=False, blank=False, db_index=True, default=lambda:datetime.datetime.now(pytz.utc))

    def __unicode__(self):
        return "%s" % (self.datetime,)

    def get_absolute_url(self):
        return django.core.urlresolvers.reverse('appomatic_siteinfo.views.event', kwargs={'id': self.id})

    class Meta:
        ordering = ('-datetime', )

class SiteEvent(Event):
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
    operator = django.db.models.ForeignKey(Operator, related_name="events")

    def __unicode__(self):
        return "%s @ %s for %s" % (self.datetime, self.well or self.site, self.operator)


class OperatorInfoEvent(OperatorEvent):
    infourl = django.db.models.TextField(null=True, blank=True)
    info = fcdjangoutils.fields.JsonField(null=True, blank=True)

class PermitEvent(OperatorInfoEvent):
    pass

class SpudEvent(OperatorInfoEvent):
    pass

class UserEvent(SiteEvent):
    author = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="events")

    def __unicode__(self):
        return "%s @ %s for %s" % (self.datetime, self.well or self.site, self.author)

class CommentEvent(UserEvent):
    content = ckeditor.fields.RichTextField(verbose_name="Comment", config_name='small')




class CommentForm(django.forms.ModelForm):
    class Meta:
        model = CommentEvent
        fields = ['content']


# Map template
 
class MapTemplate(appomatic_mapserver.maptemplates.MapTemplateSimple):
    name = "SiteInfo site"
    
    def row_generate_text(self, row):
        row['url'] = django.core.urlresolvers.reverse('appomatic_siteinfo.views.site', kwargs={'id': row['id']})
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
