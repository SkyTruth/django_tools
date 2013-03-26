import appomatic_mapserver.mapsources
import appomatic_mapserver.maptemplates
import appomatic_mapserver.models

class MapLayer(object):
    def __init__(self, urlquery):
        self.urlquery = urlquery
        self.layerdef = appomatic_mapserver.models.Layer.objects.get(slug=self.urlquery['layer'], application__slug=self.urlquery['application'])
        self.template = appomatic_mapserver.maptemplates.MapTemplate(self, urlquery)
        self.source = appomatic_mapserver.mapsources.MapSource(self, urlquery)
