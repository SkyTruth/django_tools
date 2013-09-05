import django.db.models
import fcdjangoutils.fields
import appomatic_mapserver.mapsources
import appomatic_mapserver.maptemplates
import django.utils.functional
import fcdjangoutils.fields

def set_path(d, path, value):
    node = d
    for item in path[:-1]:
        if item not in node:
            node[item] = {}
        node = node[item]
    node[path[-1]] = value

class BaseApplication(object):
    def __new__(cls, urlquery, *arg, **kw):
        if cls is BaseApplication:
            app = urlquery['application']
            if app in BuiltinApplication.implementations:
                return BuiltinApplication.implementations[app](urlquery, *arg, **kw)
            else:
                return Application.objects.get(slug=app)
        else:
            return object.__new__(cls, urlquery, *arg, **kw)

    @property
    def layer_defs(self):
        defs = {}
        for layer in self.get_layers():
            defs[layer.name] = layer.layer_def
        return defs

    def get_layer(self, urlquery):
        raise NotImplementedError

    def get_layers(self):
        raise NotImplementedError

class BaseLayer(object):
    TYPES = {
        'MapServer.Layer.Db': 'Database backed layer',
    }
    TYPES_LIST = TYPES.items()
    TYPES_LIST.sort()

    @property
    def layer_def(self):
        definition = self.definition or {}

        for name in ('name', 'slug', 'type'):
            definition[name] = getattr(self, name)

        # This is sent back to the server from the front-end and is used to find this layer object again
        set_path(definition, ['options', 'protocol', 'params', 'layer'], self.slug)

        return definition

    def __unicode__(self):
        return self.name


class BuiltinApplication(BaseApplication):
    implementations = {}
    name = 'Unnamed buitlin application'
    configuration = {}

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            module = members.get('__module__', '__main__')
            if name != "BuiltinApplication" or module != "appomatic_mapserver.models":
                BuiltinApplication.implementations[members.get('__module__', '__main__') + "." + name] = cls

    def __init__(self, urlquery):
        self.urlquery = urlquery

    @property
    def slug(self):
        t = type(self)
        return "%s.%s" % (t.__module__, t.__name__)

class BuiltinLayer(BaseLayer):
    name = "Unnamed layer"
    type = "MapServer.Layer.Db"
    backend_type = "appomatic_mapserver.mapsources.TolerancePathMap"
    template = "appomatic_mapserver.maptemplates.MapTemplateCog"
    query = ""
    definition = {}

    @property
    def slug(self):
        t = type(self)
        return "%s.%s" % (t.__module__, t.__name__)

    def __init__(self, application):
        self.application = application


class Application(BaseApplication, django.db.models.Model):
    slug = django.db.models.SlugField(max_length=1024, primary_key=True)
    name = django.db.models.CharField(max_length=1024, unique=True)
    configuration = fcdjangoutils.fields.JsonField(max_length=2048, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_layer(self, urlquery):
        return self.layers.get(slug=urlquery['layer'])

    def get_layers(self):
        return self.layers.all()

class Layer(BaseLayer, django.db.models.Model):
    application = django.db.models.ForeignKey(Application, related_name="layers")

    slug = django.db.models.SlugField(max_length=1024, primary_key=True)
    name = django.db.models.CharField(max_length=1024, unique=True)


    type = django.db.models.CharField(
        max_length=1024,
        choices=BaseLayer.TYPES_LIST,
        default='MapServer.Layer.Db')

    backend_type = django.db.models.CharField(
        max_length=1024,
        choices=[],
        default='appomatic_mapserver.mapsources.TolerancePathMap')

    template = django.db.models.CharField(
        max_length=1024,
        choices=[],
        default='appomatic_mapserver.maptemplates.MapTemplateCog')

    query = django.db.models.TextField(max_length=1024)

    definition = fcdjangoutils.fields.JsonField(blank=True)

    def __init__(self, *args, **kwargs):
        super(Layer, self).__init__(*args, **kwargs)

        def get_backend_types():
            types = [(id, obj.name)
                          for (id, obj) in appomatic_mapserver.mapsources.MapSource.implementations.iteritems()]
            types.sort()
            return types
        def get_templates():
            templates = [(id, obj.name)
                         for (id, obj) in appomatic_mapserver.maptemplates.MapTemplate.implementations.iteritems()]
            templates.sort()
            return templates

        self._meta.get_field_by_name('backend_type')[0]._choices = django.utils.functional.lazy(get_backend_types, list)()
        self._meta.get_field_by_name('template')[0]._choices = django.utils.functional.lazy(get_templates, list)()


class GridSnappingMapCache(django.contrib.gis.db.models.Model):
    query = django.db.models.TextField(db_index=True)
    snaplevel = django.db.models.IntegerField(db_index=True)

class GridSnappingMapCacheData(django.contrib.gis.db.models.Model):
    cache = django.db.models.ForeignKey(GridSnappingMapCache, related_name="data")
    location = django.contrib.gis.db.models.GeometryField(null=True, blank=True, db_index=True)
    count = django.db.models.IntegerField(default = 0)

