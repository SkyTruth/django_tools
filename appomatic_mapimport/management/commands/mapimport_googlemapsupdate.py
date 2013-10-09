import django.core.management.base
import optparse
import contextlib
import django.db
import httplib2
import sys
import os
import os.path
import appomatic_mapimport.mapimport
import datetime
from django.conf import settings
import lxml.etree
import datetime
import zipfile
import fastkml.kml
import pytz
import StringIO

KML_ROOT = os.path.join(settings.MEDIA_ROOT, "googlemaps")


class Command(appomatic_mapimport.mapimport.Import):
    SRC = 'GOOGLEMAPS'
    help = 'Import update areas from Google maps'

    starturl = "http://mw1.google.com/mw-earth-vectordb/Imagery_Updates/latest_update.kml"

    def connectioninfo(self):
        raise NotImplementedError

    @contextlib.contextmanager
    def connect(self):
        h = httplib2.Http()
        resp, content = h.request(self.starturl, "GET")
        if not resp['status'] == '200':
            raise Exception(resp)

        self.connection = lxml.etree.fromstring(content)
        yield self.connection

    def listfiles(self):
        return self.connection.xpath(".//kml:NetworkLink/kml:Link/kml:href/text()", namespaces={"kml": "http://www.opengis.net/kml/2.2"})

    def download(self, filepath):
        # Download KMZ-file
        h = httplib2.Http()
        resp, filecontent = h.request(filepath, "GET")
        if not resp['status'] == '200':
            raise Exception(resp)

        with open(self.localpath(filepath), "w") as f:
            f.write(filecontent)

        self.currentfile = filepath

    def loadfile(self, file):
        with zipfile.ZipFile(file) as zfile:
            filedate = datetime.datetime.strptime(os.path.split(self.currentfile)[1].split("_")[0], "%m-%d-%Y")

            kmlfile = [name for name in zfile.namelist() if name.endswith(".kml")][0]
            k = fastkml.kml.KML()
            with zfile.open(kmlfile) as f:
                # Split long coordinates lines to make xml parsing not fail...
                def mangleline(line):
                    if "<" in line or ">" in line:
                        return line
                    return line.replace(" ", "\n")
                k.from_string('\n'.join(mangleline(l) for l in f.read().split("\n")))

            def collect(feature):
                if hasattr(feature, "features"):
                    for sub in feature.features():
                        for change in collect(sub): yield change
                elif isinstance(feature, fastkml.kml.Placemark):
                    try:
                        geomtype = feature.geometry.type
                    except Exception, e:
                        print "Unknown geometry type: %s" % (e,)
                        return
                    geoms = []
                    if geomtype == 'Polygon':
                        geoms = [feature.geometry]
                    elif geomtype == 'MultiPolygon':
                        geoms = feature.geometry.geoms
                    else:
                        print "Unknown geometry type: %s" % (geomtype,)
                        return
                    
                    for geom in geoms:
                        if hasattr(geom, "x"):
                            x, y = geom.x, geom.y
                        elif hasattr(geom, "centroid"):
                            x, y = geom.centroid.x, geom.centroid.y
                        else:
                            return
                        yield {
                            'datetime': filedate,
                            'longitude': x,
                            'latitude': y,
                            'location': geom.to_wkt(),
                            'geom': geom,
                            'quality': 1
                            }
            for change in collect(k): yield change

    def insertrow(self, row):
        try:
            self.cur.execute("""
                        insert into appomatic_mapdata_updateregion (
                          "src",
                          "srcfile",
                          "datetime",
                          "latitude",
                          "longitude",
                          "location",
                          "quality")
                        values (
                          'GOOGLEMAPS',
                          %(filename)s,
                          %(datetime)s,
                          %(latitude)s,
                          %(longitude)s,
                          ST_Simplify(ST_GeomFromText(%(location)s, 4326), 0.04), -- ~2M should be good enough for this...
                          %(quality)s)""",
                        row)
        except:
            if False:
                import tempfile
                handle, filepath = tempfile.mkstemp(".kml")
                with os.fdopen(handle, "w") as f:
                    k = fastkml.kml.KML()
                    ns = '{http://www.opengis.net/kml/2.2}'
                    d = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
                    k.append(d)
                    p = fastkml.kml.Placemark(ns, 'id', 'name', 'description')
                    p.geometry = row['geom']
                    d.append(p)
                    f.write(k.to_string(prettyprint=True))
                print "ERROR DUMPED TO %s" % filepath
            raise
