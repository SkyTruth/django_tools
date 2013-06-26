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
import lxml.html.soupparser
import datetime
import zipfile
import fastkml.kml
import pytz
import StringIO

KML_ROOT = os.path.join(settings.MEDIA_ROOT, "nightfire")


class Command(appomatic_mapimport.mapimport.Import):
    SRC = 'VIIRS'
    help = 'Import data from VIIRS'

    # Included in an iframe at http://ngdc.noaa.gov/eog/viirs/download_viirs_fire.html
    starturl = "http://ngdc.noaa.gov/eog/viirs/download_viirs_fire_iframe_cor.html"
    baseurl = os.path.dirname(starturl)


    def connectioninfo(self):
        raise NotImplementedError

    @contextlib.contextmanager
    def connect(self):
        h = httplib2.Http()
        resp, content = h.request(self.starturl, "GET")
        if not resp['status'] == '200':
            raise Exception(resp)
        content = content.replace('\0', '')
        print "bugfixed"
        self.connection = lxml.html.soupparser.fromstring(content)
        print "parsed"
        yield content

    def listfiles(self):
        for entry in self.connection.xpath(".//ul[@class='treeview']/li/ul/li"):
            yield entry.xpath("a[text()='KMZ']/@href")[0]

    def download(self, filepath):
        # Download KMZ-file
        h = httplib2.Http()
        resp, filecontent = h.request(filepath, "GET")
        if not resp['status'] == '200':
            raise Exception(resp)

        with open(self.localpath(filepath), "w") as f:
            f.write(filecontent)

    def loadfile(self, file):
        with zipfile.ZipFile(file) as zfile:
            kmlfile = [name for name in zfile.namelist() if name.endswith(".kml")][0]
            k = fastkml.kml.KML()
            with zfile.open(kmlfile) as f:
                k.from_string(f.read())

            kmldoc = k.features().next()

            for feature in kmldoc.features():
                if not isinstance(feature, fastkml.kml.Placemark): continue
                if not feature.description: continue

                icon_href = None
                for style in feature.styles():
                    for style2 in style.styles():
                        if hasattr(style2, "icon_href"):
                            icon_href = style2.icon_href

                description = lxml.html.soupparser.fromstring(feature.description)

                # Some ugly hack to parse their info popups...
                detection = dict(row.split("=")
                                 for row in description.xpath(".//tr/td/text()")
                                 if row.count("=") == 1)

                detection['name'] = feature.name or ""
                detection['longitude'] = feature.geometry.x
                detection['latitude'] = feature.geometry.y
                detection['location'] = feature.geometry.to_wkt()                                                
                detection['quality'] = [1, 0][icon_href == "http://maps.google.com/mapfiles/marker_white.png"] # White means curve fitting failed, so quality is shit...

                # Example:
                # {'Radiant output': '3.92 W/m2',
                #  'Temperature': '1944 deg. K',
                #  'Radiative heat': '10.75 MW',
                #  'VIIRS band M10 raw DN': '418 ',
                #  'Time': '28-Feb-2013 01:08:48',
                #  'Source footprint': '13.28 m2',
                #  'Sat zenith angle': '70.14',
                #  'Source ID': 'SVM10_npp_d20130228_t0104572_e0110376_IR_source_1'}

                if 'Time' in detection:
                    value = detection.pop('Time')
                    detection['datetime'] = datetime.datetime.strptime(value, '%d-%b-%Y %H:%M:%S').replace(tzinfo=pytz.utc)
                else:
                    detection['datetime'] = date

                # Normalize and remove units
                self.getFloat(detection, 'RadiantOutput', ('Radiant output','Radiant heat intensity'), {'W/m2': 1.0, 'W/cm2': 0.0001})
                self.getFloat(detection, 'Temperature', ('Temperature',), {'deg. K': 1.0})
                self.getFloat(detection, 'RadiativeHeat', ('Radiative heat','Radiant heat'), {'MW': 1.0})
                self.getFloat(detection, 'footprint', ('Source footprint heat','Source footprint'), {'m2': 1.0, 'cm2': 0.0001})
                self.getFloat(detection, 'SatZenithAngle', ('Sat zenith angle',), {'': 1.0})

                if 'Source ID' in detection:
                    detection['SourceID'] = detection.pop('Source ID')
                else:
                    detection['SourceID'] = ""

                if not detection['Temperature']:
                    print feature.description

                yield detection

    def insertrow(self, row):
        self.cur.execute("""
                    insert into appomatic_mapdata_viirs (
                      "src",
                      "srcfile",
                      "datetime",
                      "name",
                      "latitude",
                      "longitude",
                      "location",
                      "RadiantOutput",
                      "Temperature",
                      "RadiativeHeat",
                      "footprint",
                      "SatZenithAngle",
                      "SourceID",
                      "quality")
                    values (
                      'VIIRS',
                      %(filename)s,
                      %(datetime)s,
                      %(name)s,
                      %(latitude)s,
                      %(longitude)s,
                      ST_GeomFromText(%(location)s, 4326),
                      %(RadiantOutput)s,
                      %(Temperature)s,
                      %(RadiativeHeat)s,
                      %(footprint)s,
                      %(SatZenithAngle)s,
                      %(SourceID)s,
                      %(quality)s)""",
                    row)


    def getFloat(self, row, dstname, srcnames, suffixtable, empty = None):
        value = empty
        for srcname in srcnames:
            if srcname in row:
                value = row.pop(srcname)
                suffix = ''
                if ' ' in value:
                    value, suffix = value.split(' ', 1)
                    suffix = suffix.strip()
                value = float(value.strip())
                value *= suffixtable[suffix]
        row[dstname] = value
