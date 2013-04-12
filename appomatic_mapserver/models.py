import django.db.models
import fcdjangoutils.fields
import appomatic_mapserver.mapsources
import appomatic_mapserver.maptemplates
import django.utils.functional

def set_path(d, path, value):
    node = d
    for item in path[:-1]:
        if item not in node:
            node[item] = {}
        node = node[item]
    node[path[-1]] = value


class Application(django.db.models.Model):
    slug = django.db.models.SlugField(max_length=1024, primary_key=True)
    name = django.db.models.CharField(max_length=1024, unique=True)

    def __unicode__(self):
        return self.name

    @property
    def layer_defs(self):
        defs = {}
        for layer in self.layers.all():
            defs[layer.name] = layer.layer_def
        return defs

class Layer(django.db.models.Model):
    application = django.db.models.ForeignKey(Application, related_name="layers")

    slug = django.db.models.SlugField(max_length=1024, primary_key=True)
    name = django.db.models.CharField(max_length=1024, unique=True)


    TYPES = {
        'MapServer.Layer.Db': 'Database backed layer',
    }
    TYPES_LIST = TYPES.items()
    TYPES_LIST.sort()
    type = django.db.models.CharField(
        max_length=1024,
        choices=TYPES_LIST,
        default='appomatic_mapserver.views.TolerancePathMap')

    backend_type = django.db.models.CharField(
        max_length=1024,
        choices=[],
        default='appomatic_mapserver.views.TolerancePathMap')

    template = django.db.models.CharField(
        max_length=1024,
        choices=[],
        default='appomatic_mapserver.views.MapTemplateCog')

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
