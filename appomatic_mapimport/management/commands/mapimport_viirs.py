import django.core.management.base
import optparse
import contextlib
import django.db
import httplib2
import sys
import os
import os.path
import appomatic_mapimport.ksat
import datetime
from django.conf import settings
import lxml.html.soupparser
import datetime
import zipfile
import fastkml.kml
import pytz
import StringIO

KML_ROOT = os.path.join(settings.MEDIA_ROOT, "nightfire")


class Command(django.core.management.base.BaseCommand):
    help = 'Import data from exact earth'

    def handle(self, *args, **options):
        try:
            self.handle2(*args, **options)
        except Exception, e:
            import traceback
            print e
            traceback.print_exc()
            raise

    starturl = "http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html"
    baseurl = os.path.dirname(starturl)

    def handle2(self, *args, **options):
        with contextlib.closing(django.db.connection.cursor()) as cur:

            cur.execute("select filename from appomatic_mapimport_downloaded where src='VIIRS'");
            oldfiles = set(row[0] for row in cur.fetchall())

            h = httplib2.Http()
            resp, content = h.request(self.starturl, "GET")
            if not resp['status'] == '200':
                raise Exception(resp)
            content = content.replace('\0', '')
            print "bugfixed"
            content = lxml.html.soupparser.fromstring(content)
            print "parsed"
            for entry in content.xpath(".//ul[@class='treeview']/li/ul/li"):
                date = entry.xpath("text()[1]")[0]
                url = entry.xpath("a[text()='KMZ']/@href")[0]

                # Americans using a sane date format... who would have thought? YearMonthDay (but no separator)
                date = datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8])).replace(tzinfo=pytz.utc)
            
                url = self.baseurl + '/' + url

                filename = os.path.basename(url)[:-len(".kmz")]
                
                if filename in oldfiles:
                    print url + " (OLD)"
                else:
                    print url

                    cur.execute("begin")
                    try:
                        # Download KMZ-file
                        h = httplib2.Http()
                        resp, filecontent = h.request(url, "GET")
                        if not resp['status'] == '200':
                            raise Exception(resp)

                        localpath = os.path.join(KML_ROOT, date.strftime("%Y-%m-%d %H:%M:%S"))
                        try:
                            os.makedirs(localpath)
                        except:
                            pass
                        with zipfile.ZipFile(StringIO.StringIO(filecontent)) as zfile:
                            zfile.extractall(localpath)

                        # Normalize name of kml file...
                        localkmlpath = os.path.join(localpath, "doc.kml")
                        kmlfile = [name for name in os.listdir(localpath) if name.endswith(".kml")][0]
                        os.rename(os.path.join(localpath, kmlfile), localkmlpath)

                        k = fastkml.kml.KML()
                        with open(localkmlpath) as f:
                            k.from_string(f.read())

                        kmldoc = k.features().next()

                        for feature in kmldoc.features():
                            if not isinstance(feature, fastkml.kml.Placemark): continue
                            description = lxml.html.soupparser.fromstring(feature.description)

                            # Some ugly hack to parse their info popups...
                            detection = dict(row.split("=")
                                             for row in description.xpath(".//tr/td/text()")
                                             if row.count("=") == 1)

                            detection['filename'] = filename
                            detection['name'] = feature.name or ""
                            detection['longitude'] = feature.geometry.x
                            detection['latitude'] = feature.geometry.y
                            detection['location'] = feature.geometry.to_wkt()                                                
                            
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

                            def getFloat(dstname, srcname, suffixtable, empty = None):
                                if srcname in detection:
                                    value = detection.pop(srcname)
                                    suffix = ''
                                    if ' ' in value:
                                        value, suffix = value.split(' ', 1)
                                        suffix = suffix.strip()
                                    value = float(value.strip())
                                    value *= suffixtable[suffix]
                                else:
                                    value = empty
                                detection[dstname] = value


                            # Normalize and remove units
                            getFloat('RadiantOutput', 'Radiant output', {'W/m2': 1.0, 'W/cm2': 0.0001})
                            getFloat('Temperature', 'Temperature', {'deg. K': 1.0})
                            getFloat('RadiativeHeat', 'Radiative heat', {'MW': 1.0})
                            getFloat('footprint', 'Source footprint heat', {'m2': 1.0, 'cm2': 0.0001})
                            getFloat('SatZenithAngle', 'Sat zenith angle', {'': 1.0})

                            if 'Source ID' in detection:
                                detection['SourceID'] = detection.pop('Source ID')
                            else:
                                detection['SourceID'] = ""

                            if not detection['Temperature']:
                                print feature.description

                            try:
                                cur.execute("""
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
                                              "SourceID")
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
                                              %(SourceID)s)""",
                                            detection)
                            except:
                                print detection
                                raise

                        cur.execute("insert into appomatic_mapimport_downloaded (src, filename) values ('VIIRS', %(filename)s)", {'filename': filename})

                    except Exception, e:
                        cur.execute("rollback")
                        print "    Unable to open file: %s: %s" % (str(type(e)), str(e))
                        import traceback
                        traceback.print_exc()
                        raise
                    else:
                        cur.execute("commit")

