import appomatic_mapserver.maplayer
try:
    import shapely.wkt
    load_wkt = shapely.wkt.loads
except:
    import pygeoif.geometry
    load_wkt = pygeoif.geometry.from_wkt
import fastkml.kml
import fastkml.geometry
import geojson
import fcdjangoutils.jsonview
import uuid
import django.http
import types
import cgi
import itertools
import contextlib
import django.template.defaultfilters

def flattentree(tree):
    if isinstance(tree, types.GeneratorType):
        for item in tree:
            for result in flattentree(item):
                yield result
    else:
        yield tree

@contextlib.contextmanager
def nestedwith(*mgrs):
    if mgrs:
        with mgrs[0] as value:
            with nestedwith(*mgrs[1:]) as values:
                yield (value,) + values
    else:
        yield ()

class Peekable(object):
    def __init__(self, iterator):
        self.iterator = iter(iterator)
        self.values = []
    def __iter__(self):
        return self
    def next(self):
        if self.values:
            value = self.values[0]
            self.values = self.values[1:]
            return value
        else:
            return self.iterator.next()
    def peek(self, items):
        """Returns the next items number of items from the stream,
        retaining the position within the stream (with regards to next()).
        If StopIteration is reached on the underlying stream
        a list shorter than items number of items will be returned.
        """

        for i in xrange(len(self.values), items):
            try:
                self.values.append(self.iterator.next())
            except StopIteration:
                pass
        return self.values[:items]

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
        self.application = appomatic_mapserver.models.BaseApplication(self.urlquery)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def get_layers(self):
        if 'layer' in self.urlquery:
            yield appomatic_mapserver.maplayer.MapLayer(self.application, self.urlquery)
        else:
            for name, layer in self.get_layer_defs().iteritems():
                urlquery = dict(self.urlquery)
                urlquery.update(layer['options']['protocol']['params'])
                urlquery['name'] = name
                yield appomatic_mapserver.maplayer.MapLayer(self.application, urlquery)

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
        if timeframe['timemin'] is None:
            timeframe['timemin'] = 0
        if timeframe['timemax'] is None:
            timeframe['timemax'] = timeframe['timemin']
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
                        geometry = load_wkt(str(row['shape']))
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
    def __init__(self, *arg, **kw):
        MapRenderer.__init__(self, *arg, **kw)
        self.group_value_path = []

    def update_group_value_path(self, group_value_path):
        matching = 0

        for (old, new) in itertools.izip(self.group_value_path, group_value_path):
            if old != new:
                break
            matching += 1

        for i in xrange(matching, len(self.group_value_path)):
            yield "</kml:Folder>"

        for i in xrange(matching, len(group_value_path)):
            yield '<kml:Folder id="group-%s">' % '-'.join(django.template.defaultfilters.slugify(("%s" % item).strip()) for item in group_value_path[:i])
            yield '<kml:name>%s</kml:name>' % group_value_path[i]
            yield '<kml:visibility>1</kml:visibility>'

        self.group_value_path = group_value_path

    def merge_layers(self, *layers):
        with nestedwith(*(layer.source for layer in layers)) as sources:
            layers = dict((layer.layerdef.slug,
                           {'layer': layer,
                            'source': source,
                            'rows': Peekable(source.get_map_data())})
                          for (layer, source) in zip(layers, sources))

            def remove_empty_layers():
                # Remove layers that have run out of rows:
                for slug, layer in layers.items():
                    if not layer['rows'].peek(1):
                        del layers[slug]
                        continue

            remove_empty_layers()

            for slug, layer in layers.iteritems():
                row = layer['rows'].peek(1)[0]
                layer['groupings'] = len([key for key in row.keys() if key.startswith('grouping')])
                layer['groupingcols'] = ["grouping%s" % ind for ind in xrange(0, layer['groupings'])]

            while layers:
                def layercmp(a, b):
                    # Compare the next rows from two layers, which should come first?

                    layera = layers[a]
                    layerb = layers[b]

                    rowa = layera['rows'].peek(1)[0]
                    rowb = layerb['rows'].peek(1)[0]
                    colsa = [rowa[col] for col in layera['groupingcols']]
                    colsb = [rowb[col] for col in layerb['groupingcols']]

                    return cmp(colsa, colsb)

                nextslug = sorted(layers.keys(), cmp=layercmp, reverse=True)[0]
                if nextslug in layers: # Check for end of all layers
                    layer = layers[nextslug]
                    row = layer['rows'].next()
                    path = [row[col] for col in layer['groupingcols']]
                    yield layer['layer'], path, row

                remove_empty_layers()


    def get_map(self):
        def get_map():
            yield '<kml:kml xmlns:kml="http://www.opengis.net/kml/2.2">'
            yield '<kml:Document id="docid">'

            yield '<kml:name>doc name</kml:name>'
            yield '<kml:description>doc name</kml:description>'
            yield '<kml:visibility>1</kml:visibility>'

            for layer in self.get_layers():
                yield layer.template.kml_style()

            self.group_value_path = []

            for layer, path, row in self.merge_layers(*self.get_layers()):
                yield self.update_group_value_path(path)

                layer.template.row_generate_text(row)

                yield '<kml:Placemark id="%s">' % row['title']
                yield '<kml:name>%s</kml:name>' % row['title']
                yield '<kml:description>%s</kml:description>' % cgi.escape(row['description'])
                yield '<kml:visibility>1</kml:visibility>'
                yield layer.template.row_kml_style(row)
                yield fastkml.geometry.Geometry(geometry = load_wkt(str(row['shape']))).to_string()

                if 'timemax' in row and 'timemin' in row:
                    yield "<TimeSpan><begin>%s</begin><end>%s</end></TimeSpan>" % (row['timemin'].strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                                                   row['timemax'].strftime("%Y-%m-%dT%H:%M:%SZ"))
                else:
                    yield "<TimeStamp><when>%s</when></TimeStamp>" % (row['datetime_time'].strftime("%Y-%m-%dT%H:%M:%SZ"))

                yield '</kml:Placemark>'

            yield self.update_group_value_path([])

            yield '</kml:Document>'
            yield '</kml:kml>'

        res = django.http.StreamingHttpResponse(
            flattentree(get_map()),
            mimetype="application/vnd.google-earth.kml+xml",
            status=200)
        res['Content-disposition'] = 'attachment; filename=export.kml'
        return res
