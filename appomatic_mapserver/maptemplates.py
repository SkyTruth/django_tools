import fastkml.kml
import fastkml.styles
import uuid
import monkeypatches.fastkmlmonkey

KMLNS = '{http://www.opengis.net/kml/2.2}'

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
        self.kmlstyles = {}

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            module = members.get('__module__', '__main__')
            if name != "MapTemplate" or module != "appomatic_mapserver.maptemplates":
                MapTemplate.implementations[module + "." + name] = cls

class MapTemplateSimple(MapTemplate):
    name = 'Simple template'

    def row_generate_text(self, row):
        row['title'] = row.get(
            'title',
            row.get(
                'name',
                row.get(
                    'mmsi',
                    "%s @ %sN %sE" % (row.get('id', ''),
                                      row.get('longitude', ''),
                                      row.get('latitude', '')))))

        if "url" in row:
            header = "<h2><a href='%(url)s'>%(name)s</a></h2>"
        cols = [col for col in row.keys() if col not in ("shape", "location")]
        cols.sort()
        template = '<table>%s</table>' % ''.join("<tr><th>%s</th><td>%%(%s)s</td></tr>" % (col, col) for col in cols)
        row['description'] = template % row

        row['style'] = {
          "graphicName": "circle",
          "fillOpacity": 1.0,
          "fillColor": "#0000ff",
          "strokeOpacity": 1.0,
          "strokeColor": "#ff0000",
          "strokeWidth": 1,
          "pointRadius": 3,
          }
    
    def row_kml_style(self, row, doc):
        if 'stdstyle' not in self.kmlstyles:
            style = fastkml.styles.Style(KMLNS, "style-simple-normal")
            style.append_style(fastkml.styles.IconStyle(
                    KMLNS,
                    "style-simple-normal-icon",
                    scale=0.5,
                    icon_href="http://alerts.skytruth.org/markers/red-x.png"))
            style.append_style(fastkml.styles.LabelStyle(
                    KMLNS,
                    "style-simple-normal-label",
                    scale=0))
            doc.append_style(style)

            style = fastkml.styles.Style(KMLNS, "style-simple-highlight")
            style.append_style(fastkml.styles.IconStyle(
                    KMLNS,
                    "style-simple-highlight-icon",
                    scale=1.0,
                    icon_href="http://alerts.skytruth.org/markers/red-x.png"))
            style.append_style(fastkml.styles.LabelStyle(
                    KMLNS,
                    "style-simple-highlight-label",
                    scale=1))
            doc.append_style(style)

            style_map = fastkml.styles.StyleMap(
                KMLNS,
                "style-simple")
            style_map.normal = fastkml.styles.StyleUrl(KMLNS, url="#style-simple-normal")
            style_map.highlight = fastkml.styles.StyleUrl(KMLNS, url="#style-simple-highlight")
            doc.append_style(style_map)

            self.kmlstyles['stdstyle'] = "#style-simple"

        return self.kmlstyles['stdstyle']

class MapTemplateCog(MapTemplateSimple):
    name = 'Template for events with COG'
    def row_kml_style(self, row, doc):
        id = row.get('id', row.get('mmsi', str(uuid.uuid4())))

        try:
            c = min(float(row['sog']), 15) * 17
        except:
            c = 0
        color = 'ff00%02x%02x' % (c, 255-c)

        style = fastkml.styles.Style(KMLNS, "style-%s-normal" % (id,))
        style.append_style(fastkml.styles.IconStyle(
            KMLNS,
            "style-%s-normal-icon" % id,
            icon_href = "http://alerts.skytruth.org/markers/vessel_direction.png",
            #  <hotSpot x="16" y="3" xunits="pixels" yunits="pixels"/>
            heading = row.get('cog', 0),
            color = color,
            scale=0.5))
        style.append_style(fastkml.styles.LabelStyle(
                KMLNS,
                "style-%s-normal-label" % (id,),
                scale=0))
        doc.append_style(style)

        style = fastkml.styles.Style(KMLNS, "style-%s-highlight" % (id,))
        style.append_style(fastkml.styles.IconStyle(
            KMLNS,
            "style-%s-highlight-icon" % id,
            icon_href = "http://alerts.skytruth.org/markers/vessel_direction.png",
            #  <hotSpot x="16" y="3" xunits="pixels" yunits="pixels"/>
            heading = row.get('cog', 0),
            color = color,
            scale=1.0))
        style.append_style(fastkml.styles.LabelStyle(
                KMLNS,
                "style-%s-highlight-label" % (id,),
                scale=1))
        doc.append_style(style)

        style_map = fastkml.styles.StyleMap(
            KMLNS,
            "style-%s" % (id,))
        style_map.normal = fastkml.styles.StyleUrl(KMLNS, url="#style-%s-normal" % (id,))
        style_map.highlight = fastkml.styles.StyleUrl(KMLNS, url="#style-%s-highlight" % (id,))
        doc.append_style(style_map)

        return "#style-%s" % (id,)
