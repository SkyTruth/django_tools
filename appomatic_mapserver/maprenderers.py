import appomatic_mapserver.maplayer
import shapely.geometry
import shapely.wkb
import shapely.wkt
import fastkml.kml
import geojson
import fcdjangoutils.jsonview
import uuid
import django.http

class MapRenderer(object):
    implementations = {}

    def __new__(cls, urlquery, *arg, **kw):
        if cls is MapRenderer:
            type = urlquery.get('format', 'appomatic_mapserver.maprenderers.MapRendererGeojson')
            return cls.implementations[type](urlquery, *arg, **kw)
        else:
            return object.__new__(cls, urlquery, *arg, **kw)

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            module = members.get('__module__', '__main__')
            if name != "MapRenderer" or module != "appomatic_mapserver.maprenderers":
                MapRenderer.implementations[members.get('__module__', '__main__') + "." + name] = cls

    def __init__(self, urlquery):
        self.urlquery = urlquery
        self.application = appomatic_mapserver.models.Application.objects.get(slug=self.urlquery['application'])

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def get_layers(self):
        if 'layer' in self.urlquery:
            yield appomatic_mapserver.maplayer.MapLayer(self.urlquery)
        else:
            for name, layer in self.get_layer_defs().iteritems():
                urlquery = dict(self.urlquery)
                urlquery.update(layer['options']['protocol']['params'])
                urlquery['name'] = name
                yield appomatic_mapserver.maplayer.MapLayer(urlquery)

    def get_timeframe(self):
        timeframe = {'timemin': None, 'timemax':None}
        for layer in self.get_layers():
            with layer.source as source:
                new = source.get_timeframe()
                if new is None: continue
                if timeframe['timemin'] is None or timeframe['timemin'] > new['timemin']:
                    timeframe['timemin'] = new['timemin']
                if timeframe['timemax'] is None or timeframe['timemax'] < new['timemax']:
                    timeframe['timemax'] = new['timemax']
        return timeframe

    def get_layer_defs(self):
        return self.application.layer_defs


class MapRendererGeojson(MapRenderer):
    def get_map(self):
        features = []

        for layer in self.get_layers():
            with layer.source as source:
                for row in source.get_map_data():
                    layer.template.row_generate_text(row)
                    try:
                        geometry = shapely.wkt.loads(str(row['shape']))
                    except Exception, e:
                        e.args += (row['shape'],)
                        raise e
                    geometry = fcdjangoutils.jsonview.from_json(
                        geojson.dumps(
                            geometry))
                    del row['shape']
                    feature = {"type": "Feature",
                               "geometry": geometry,
                               "properties": row}
                    features.append(feature)

        res = django.http.HttpResponse(
            fcdjangoutils.jsonview.to_json(
                {"type": "FeatureCollection",
                 "features": features}),
            mimetype="application/json",
            status=200)
        res['Content-disposition'] = 'attachment; filename=export.geojson'
        return res

class MapRendererKml(MapRenderer):
    def get_map(self):
        kml = fastkml.kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
        kml.append(doc)

        for layer in self.get_layers():
            layer_name = layer.urlquery.get('name', str(uuid.uuid4()))
            folder = fastkml.kml.Folder(ns, "group-%s" % layer_name, layer_name)
            doc.append(folder)

            with layer.source as source:
                groupings = -1
                groupValuePath = []
                groupValueMapPath = []
                for row in source.get_map_data():
                    if groupings == -1:
                        groupings = len([key for  key in row.keys() if key.startswith('grouping')])
                        groupValuePath = ['__DUMMY__'] * groupings # Fill the path with dummy values 
                        groupValueMapPath = ['__DUMMY__'] * groupings
                        print "LAYER", layer_name, groupings
                    for ind in range(0, groupings):
                        if groupValuePath[ind] != row["grouping%s" % ind]:
                            for ind2 in range(ind, groupings):
                                groupValuePath[ind2] = row["grouping%s" % ind2]
                                groupValueMapPath[ind2] = fastkml.kml.Folder(
                                    ns,
                                    "group-%s-%s" % (layer_name, '-'.join("%s" % item for item in groupValuePath)),
                                    "%s" % row["grouping%s" % ind2])
                                if ind2 == 0:
                                    folder.append(groupValueMapPath[ind2])
                                else:
                                    groupValueMapPath[ind2-1].append(groupValueMapPath[ind2])
                            break

                    layer.template.row_generate_text(row)
                    geometry = shapely.wkt.loads(str(row['shape']))
                    placemark = fastkml.kml.Placemark(
                        ns, row['title'],
                        row['title'],
                        row['description'])
                    placemark.styleUrl = layer.template.row_kml_style(row, doc)
                    placemark.geometry = geometry
                    if groupings > 0:
                        groupValueMapPath[-1].append(placemark)
                    else:
                        folder.append(placemark)

        res = django.http.HttpResponse(
            kml.to_string(prettyprint=True),
            mimetype="application/vnd.google-earth.kml+xml",
            status=200)
        res['Content-disposition'] = 'attachment; filename=export.kml'
        return res
