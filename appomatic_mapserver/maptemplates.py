import fastkml.kml
import fastkml.styles
import uuid

class MapTemplate(object):
    implementations = {}

    def __new__(cls, layer, urlquery, *arg, **kw):
        if cls is MapTemplate:
            return cls.implementations[layer.layerdef.template](layer, urlquery, *arg, **kw)
        else:
            return object.__new__(cls, layer, urlquery, *arg, **kw)

    def __init__(self, layer, urlquery, *arg, **kw):
        self.layer = layer
        self.urlquery = urlquery

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            module = members.get('__module__', '__main__')
            if name != "MapTemplate" or module != "appomatic_mapserver.maptemplates":
                MapTemplate.implementations[module + "." + name] = cls

class MapTemplateSimple(MapTemplate):
    name = 'Simple template'
    def row_name(self, row):
        return ""

    def row_description(self, row):
        header = "<h2>%(name)s</h2>"
        if "url" in row:
            header = "<h2><a href='%(url)s'>%(name)s</a></h2>"
        cols = [col for col in row.keys() if col not in ("shape", "location")]
        cols.sort()
        template = header + '<table>%s</table>' % ''.join("<tr><th>%s</th><td>%%(%s)s</td></tr>" % (col, col) for col in cols)
        return template % row

    def group_name(self, row):
        return "%(name)s" % row

    def group_description(self, row):
        return ""
    
    def row_kml_style(self, row):
        id = row.get('id', row.get('name', row.get('mmsi', str(uuid.uuid4()))))
        style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s" % id)
        style.append_style(fastkml.styles.IconStyle(
            '{http://www.opengis.net/kml/2.2}',
            "style-item-%s-icon" % id,
            icon_href = "http://alerts.skytruth.org/markers/red-x.png"
            ))
        return style

class MapTemplateCog(MapTemplateSimple):
    name = 'Template for events with COG'
    def row_kml_style(self, row):
        id = row.get('id', row.get('name', row.get('mmsi', str(uuid.uuid4()))))
        try:
            c = min(float(row['sog']), 15) * 17
        except:
            c = 0
        color = 'ff00%02x%02x' % (c, 255-c)
        style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s" % id)
        style.append_style( fastkml.styles.IconStyle(
            '{http://www.opengis.net/kml/2.2}',
            "style-item-%s-icon" % id,
            icon_href = "http://alerts.skytruth.org/markers/vessel_direction.png",
            #  <hotSpot x="16" y="3" xunits="pixels" yunits="pixels"/>
            heading = row.get('cog', 0),
            color = color))
        return style
