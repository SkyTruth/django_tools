import django.db.models
import fcdjangoutils.fields

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

    OPTIONS_PROTOCOL_PARAMS_TYPES = {
        'appomatic_mapserver.views.TolerancePathMap': 'Simplified path',
        'appomatic_mapserver.views.EventMap': 'Event list'
    }
    OPTIONS_PROTOCOL_PARAMS_TYPES_LIST = OPTIONS_PROTOCOL_PARAMS_TYPES.items()
    OPTIONS_PROTOCOL_PARAMS_TYPES_LIST.sort()
    options_protocol_params_type = django.db.models.CharField(
        max_length=1024,
        choices=OPTIONS_PROTOCOL_PARAMS_TYPES_LIST,
        default='appomatic_mapserver.views.TolerancePathMap')

    OPTIONS_PROTOCOL_PARAMS_TEMPLATES = {
        'appomatic_mapserver.views.MapTemplateSimple': 'Simple template',
        'appomatic_mapserver.views.MapTemplateCog': 'Template for events with COG'
    }
    OPTIONS_PROTOCOL_PARAMS_TEMPLATES_LIST = OPTIONS_PROTOCOL_PARAMS_TEMPLATES.items()
    OPTIONS_PROTOCOL_PARAMS_TEMPLATES_LIST.sort()
    options_protocol_params_template = django.db.models.CharField(
        max_length=1024,
        choices=OPTIONS_PROTOCOL_PARAMS_TEMPLATES_LIST,
        default='appomatic_mapserver.views.MapTemplateCog')

    options_protocol_params_table = django.db.models.CharField(max_length=1024)

    definition = fcdjangoutils.fields.JsonField(blank=True)

    @property
    def layer_def(self):
        definition = self.definition or {}

        for member in ('type', 'options_protocol_params_type', 'options_protocol_params_template', 'options_protocol_params_table'):
            value = getattr(self, member)
            member = member.split('_')

            node = definition
            for item in member[:-1]:
                if item not in node:
                    node[item] = {}
                node = node[item]
            node[member[-1]] = value

        return definition

    def __unicode__(self):
        return self.name
