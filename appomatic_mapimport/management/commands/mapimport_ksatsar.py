import django.core.management.base
import optparse
import contextlib
import django.db
import paramiko
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

KML_ROOT = os.path.join(settings.MEDIA_ROOT, "vessel-detections")


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

    def handle2(self, *args, **options):
        with contextlib.closing(django.db.connection.cursor()) as cur:

            cur.execute("select filename from appomatic_mapimport_downloaded where src='KSATSAR'");
            oldfiles = set(row[0] for row in cur.fetchall())

            with contextlib.closing(paramiko.Transport((settings.MAPIMPORT_KSAT['host'], settings.MAPIMPORT_KSAT['port']))) as transport:
                transport.connect(username=settings.MAPIMPORT_KSAT['username'], password=settings.MAPIMPORT_KSAT['password'])
                with contextlib.closing(paramiko.SFTPClient.from_transport(transport)) as sftp:

                    sourcedir = "WWW"

                    for filename in sftp.listdir(sourcedir):
                        if filename.endswith('.kmz'):

                            filename = filename[:-len(".kmz")]
                            filepath = sourcedir + "/" + filename + ".kmz"

                            if filename in oldfiles:
                                print filepath + " (OLD)"
                            else:
                                print filepath

                                cur.execute("begin")
                                try:

                                    # Naming convention:
                                    # RS2_<yyyymmdd>_<hhmmss>_<dddd>_<Beam>_<Polarizations>_<ProductType>_<ImageID>_<Counter>_<ProcessingID>_<Customer>_<FileType>.kmz
                                    # Example name:
                                    # RS2_20130304_  013608_  0045_  SCNA_  HV_             SGF_          246437_   1644_     8280557_       SKYTRUTH_  Vessel.kmz

                                    fileinfo = dict(
                                        zip(["src", # RS2 Radarsat-2
                                             "date", # yyyymmdd Acquisition date of image
                                             "time", # hhmmss Acquisition time of image
                                             "duration", # dddd Duration of image in seconds
                                             "BeamMode", # Product beam mode.
                                             "Polarizations", # Product polarizations
                                             "ProductType", # Product type
                                             "ImageID", # Image ID
                                             "Counter", # Product counter
                                             "ProcessessingID", # Internal processor ID
                                             "Customer", #  Customer name
                                             "FileType", #  Fil Type
                                             ], 
                                            filename.split("_")))

                                    fileinfo['src'] = "KSATSAR-%(src)s" % fileinfo
                                    date = fileinfo.pop('date')
                                    time = fileinfo.pop('time')
                                    fileinfo['datetime'] = datetime.datetime(
                                        int(date[:4]), int(date[4:6]), int(date[6:8]),
                                        int(time[:2]), int(time[2:4]), int(time[4:6]))

                                    localpath = os.path.join(KML_ROOT, fileinfo['datetime'].strftime("%Y-%m-%d %H:%M:%S"))
                                    try:
                                        os.makedirs(localpath)
                                    except:
                                        pass

                                    # Download and extract kmz
                                    with contextlib.closing(sftp.file(filepath)) as file:
                                        with zipfile.ZipFile(file) as zfile:
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
                                        if not isinstance(feature, fastkml.kml.Folder) or feature.name != "Vessel": continue
                                        for subfeature in feature.features():
                                            if not isinstance(subfeature, fastkml.kml.Placemark): continue
                                            description = lxml.html.soupparser.fromstring(subfeature.description)
                                            detection = dict(item
                                                             for item in ([td.text for td in tr.findall("./td")][:2]
                                                                          for tr in description.findall(".//tr"))
                                                             if item[0].strip())
                                            detection['filename'] = filename
                                            detection['name'] = subfeature.name
                                            detection['longitude'] = subfeature.geometry.x
                                            detection['latitude'] = subfeature.geometry.y
                                            detection['location'] = subfeature.geometry.to_wkt()                                                

                                            detection.update(fileinfo)
                                            
                                            try:
                                                cur.execute("""
                                                            insert into appomatic_mapdata_sar (
                                                              "src",
                                                              "srcfile",
                                                              "datetime",
                                                              "duration",
                                                              "BeamMode",
                                                              "Polarizations",
                                                              "ProductType",
                                                              "ImageID",
                                                              "Counter",
                                                              "ProcessessingID",
                                                              "Customer",
                                                              "FileType",
                                                              "name",
                                                              "latitude",
                                                              "longitude",
                                                              "location",
                                                              "Probability",
                                                              "DetectionId",
                                                              "ProductStartTime",
                                                              "ProductStopTime",
                                                              "Beam",
                                                              "Length",
                                                              "Type",
                                                              "Heading",
                                                              "ProductId")
                                                            values (
                                                              %(src)s,
                                                              %(filename)s,
                                                              %(datetime)s,
                                                              %(duration)s,
                                                              %(BeamMode)s,
                                                              %(Polarizations)s,
                                                              %(ProductType)s,
                                                              %(ImageID)s,
                                                              %(Counter)s,
                                                              %(ProcessessingID)s,
                                                              %(Customer)s,
                                                              %(FileType)s,
                                                              %(name)s,
                                                              %(latitude)s,
                                                              %(longitude)s,
                                                              st_setsrid(st_geomfromtext(%(location)s), 4326),
                                                              %(Probability)s,
                                                              %(DetectionId)s,
                                                              %(ProductStartTime)s,
                                                              %(ProductStopTime)s,
                                                              %(Beam)s,
                                                              %(Length)s,
                                                              %(Type)s,
                                                              %(Heading)s,
                                                              %(ProductId)s)""",
                                                            detection)
                                            except:
                                                print detection
                                                raise

                                    cur.execute("insert into appomatic_mapimport_downloaded (src, filename) values ('KSATSAR', %(filename)s)", {'filename': filename})

                                except Exception, e:
                                    cur.execute("rollback")
                                    print "    Unable to open file " + str(e)
                                else:
                                    cur.execute("commit")
                                    
