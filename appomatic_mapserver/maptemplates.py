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

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            module = members.get('__module__', '__main__')
            if name != "MapTemplate" or module != "appomatic_mapserver.maptemplates":
                MapTemplate.implementations[module + "." + name] = cls

class MapTemplateSimple(MapTemplate):
    name = 'Simple template'

    excludecols = ("shape", "shape_binary", "location", "line")

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
        cols = [col for col in row.keys() if col not in self.excludecols]
        cols.sort()
        template = """
          <style>
            table th {
              text-align: right;
            }
            table th, table td {
              vertical-align: top; }
            }
          </style>
          <table>%s</table>
        """
        template = header + template % ''.join("<tr><th>%s</th><td>%%(%s)s</td></tr>" % (col, col) for col in cols)
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
    
    def kml_style(self):
        yield '<kml:StyleMap id="layerstyle-%s">' % self.layer.layerdef.slug
        yield '  <kml:Pair>'
        yield '    <kml:key>normal</kml:key>'
        yield '    <kml:Style>'
        yield '      <kml:IconStyle>'
        yield '        <kml:scale>0.5</kml:scale>'
        yield '        <kml:Icon>http://alerts.skytruth.org/markers/red-x.png</kml:Icon>'
        yield '      </kml:IconStyle>'
        yield '      <kml:LabelStyle>'
        yield '        <kml:scale>0</kml:scale>'
        yield '      </kml:LabelStyle>'
        yield '    </kml:Style>'
        yield '  </kml:Pair>'

        yield '  <kml:Pair>'
        yield '    <kml:key>highlight</kml:key>'
        yield '    <kml:Style>'
        yield '      <kml:IconStyle>'
        yield '        <kml:scale>1.0</kml:scale>'
        yield '        <kml:Icon>http://alerts.skytruth.org/markers/red-x.png</kml:Icon>'
        yield '      </kml:IconStyle>'
        yield '      <kml:LabelStyle>'
        yield '        <kml:scale>1.0</kml:scale>'
        yield '      </kml:LabelStyle>'
        yield '    </kml:Style>'
        yield '  </kml:Pair>'
        yield '</kml:StyleMap>'

    def row_kml_style(self, row):
        yield '<kml:styleUrl>#layerstyle-%s</kml:styleUrl>' % self.layer.layerdef.slug

class MapTemplateCog(MapTemplateSimple):
    name = 'Template for events with COG'
    def kml_style(self):
        yield '<kml:StyleMap id="layerstyle-%s">' % self.layer.layerdef.slug
        yield '  <kml:Pair>'
        yield '    <kml:key>normal</kml:key>'
        yield '    <kml:Style>'
        yield '      <kml:IconStyle>'
        yield '        <kml:scale>0.5</kml:scale>'
        yield '        <kml:Icon>http://alerts.skytruth.org/markers/vessel_direction.png</kml:Icon>'
        yield '      </kml:IconStyle>'
        yield '      <kml:LabelStyle>'
        yield '        <kml:scale>0</kml:scale>'
        yield '      </kml:LabelStyle>'
        yield '    </kml:Style>'
        yield '  </kml:Pair>'

        yield '  <kml:Pair>'
        yield '    <kml:key>highlight</kml:key>'
        yield '    <kml:Style>'
        yield '      <kml:IconStyle>'
        yield '        <kml:scale>1.0</kml:scale>'
        yield '        <kml:Icon>http://alerts.skytruth.org/markers/vessel_direction.png</kml:Icon>'
        yield '      </kml:IconStyle>'
        yield '      <kml:LabelStyle>'
        yield '        <kml:scale>1.0</kml:scale>'
        yield '      </kml:LabelStyle>'
        yield '    </kml:Style>'
        yield '  </kml:Pair>'
        yield '</kml:StyleMap>'


    def row_kml_style(self, row):
        id = row.get('id', row.get('mmsi', str(uuid.uuid4())))

        try:
            c = min(float(row['sog']), 15) * 17
        except:
            c = 0
        color = 'ff00%02x%02x' % (c, 255-c)

        yield '<kml:styleUrl>#layerstyle-%s</kml:styleUrl>' % self.layer.layerdef.slug
        yield '<kml:Style>'
        yield '  <kml:IconStyle>'
        yield '    <kml:heading>%s</kml:heading>' % row.get('cog', 0)
        yield '    <kml:color>%s</kml:color>' % color
        yield '    <kml:Icon>http://alerts.skytruth.org/markers/vessel_direction.png</kml:Icon>'
        yield '  </kml:IconStyle>'
        yield '</kml:Style>'

class MapTemplateCogTimeTitle(MapTemplateCog):
    name = 'Template for events with COG, titled by time'

    def row_generate_text(self, row):
        MapTemplateCog.row_generate_text(self, row)
        if 'datetime' in row:
            row['title'] = row['datetime_time'].strftime("%H:%M:%S")
class MapTemplateCogTimeTitle(MapTemplateCog):
    name = 'Template for events with COG, titled by time'

    def row_generate_text(self, row):
        MapTemplateCog.row_generate_text(self, row)
        if 'datetime' in row:
            row['title'] = row['datetime_time'].strftime("%H:%M:%S")

class MapTemplateCogDateTimeTitle(MapTemplateCog):
    name = 'Template for events with COG, titled by date & time'

    def row_generate_text(self, row):
        MapTemplateCog.row_generate_text(self, row)
        if 'datetime' in row:
            row['title'] = row['datetime_time'].strftime("%Y-%m-%d %H:%M:%S")
