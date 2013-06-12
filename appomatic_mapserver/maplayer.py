import appomatic_mapserver.mapsources
import appomatic_mapserver.maptemplates
import appomatic_mapserver.models

class MapLayer(object):
    def __init__(self, application, urlquery):
        self.application = application
        self.urlquery = urlquery
        self.layerdef = self.application.get_layer(self.urlquery)
        self.template = appomatic_mapserver.maptemplates.MapTemplate(self, urlquery)
        self.source = appomatic_mapserver.mapsources.MapSource(self, urlquery)
