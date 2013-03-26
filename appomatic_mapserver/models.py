import django.db.models
import fcdjangoutils.fields

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

    BACKEND_TYPES = {
        'appomatic_mapserver.mapsources.TolerancePathMap': 'Simplified path',
        'appomatic_mapserver.mapsources.EventMap': 'Event list'
    }
    BACKEND_TYPES_LIST = BACKEND_TYPES.items()
    BACKEND_TYPES_LIST.sort()
    backend_type = django.db.models.CharField(
        max_length=1024,
        choices=BACKEND_TYPES_LIST,
        default='appomatic_mapserver.views.TolerancePathMap')

    TEMPLATES = {
        'appomatic_mapserver.maptemplates.MapTemplateSimple': 'Simple template',
        'appomatic_mapserver.maptemplates.MapTemplateCog': 'Template for events with COG'
    }
    TEMPLATES_LIST = TEMPLATES.items()
    TEMPLATES_LIST.sort()
    template = django.db.models.CharField(
        max_length=1024,
        choices=TEMPLATES_LIST,
        default='appomatic_mapserver.views.MapTemplateCog')

    query = django.db.models.CharField(max_length=1024)

    definition = fcdjangoutils.fields.JsonField(blank=True)

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
