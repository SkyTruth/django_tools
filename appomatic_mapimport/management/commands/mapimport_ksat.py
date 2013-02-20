import django.core.management.base
import optparse
import contextlib
import django.db
import paramiko
import sys
import appomatic_mapimport.ksat
import datetime
from django.conf import settings


class Command(django.core.management.base.BaseCommand):
    help = 'Import data from exact earth'

    def handle(self, *args, **options):
        with contextlib.closing(django.db.connection.cursor()) as cur:

            cur.execute("select filename from appomatic_mapimport_downloaded where src='KSAT'");
            oldfiles = set(row[0] for row in cur.fetchall())

            with contextlib.closing(paramiko.Transport((settings.MAPIMPORT_KSAT['host'], settings.MAPIMPORT_KSAT['port']))) as transport:
                transport.connect(username=settings.MAPIMPORT_KSAT['username'], password=settings.MAPIMPORT_KSAT['password'])
                with contextlib.closing(paramiko.SFTPClient.from_transport(transport)) as sftp:

                    sourcedir = "WWW/AIS"

                    for filename in sftp.listdir(sourcedir):
                        if filename.endswith('.nmea'):

                            filename = filename[:-len(".nmea")]
                            filepath = sourcedir + "/" + filename + ".nmea"

                            if filename in oldfiles:
                                print filepath + " (OLD)"
                            else:
                                print filepath

                                try:
                                    with contextlib.closing(sftp.file(filepath)) as file:

                                        cur.execute("begin")
                                        try:

                                            for row in appomatic_mapimport.ksat.convert(file):
                                                # Why doesn't gpsdecode do scaling???
                                                if 'lon' in row: row['lon'] = row['lon'] / 600000.0 # A AIS unit is 1/10000th of a minute (1/60th of a degree)
                                                if 'lat' in row: row['lat'] = row['lat'] / 600000.0
                                                if 'C' in row:
                                                    row['C'] = datetime.datetime.fromtimestamp(int(row['C']))
                                                else:
                                                    row['C'] = None
                                                if 'S' in row:
                                                    row['S'] = 'KSAT-' + row['S']
                                                else:
                                                    row['S'] = 'KSAT'
                                                #print row
                                                #print "    %(C)s: %(mmsi)s" % row
                                                if row.get('type', None) in (1, 2, 3): # position reports
                                                    try:
                                                        cur.execute("insert into appomatic_mapdata_ais (src, datetime, mmsi, latitude, longitude, true_heading, sog, cog) values (%(S)s, %(C)s, %(mmsi)s, %(lat)s, %(lon)s, %(heading)s, %(speed)s, %(course)s)", row)
                                                    except:
                                                        print row
                                                        raise
                                                if row.get('name', None) is not None and row.get('shiptype', None) is not None:
                                                    row['url'] = 'http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=' + row['mmsi']
                                                    try:
                                                        cur.execute("insert into appomatic_mapdata_vessel (mmsi, name, type, length) select %(mmsi)s, %(shipname)s, %(shiptype)s, %(to_bow)s where %(mmsi)s not in (select mmsi from appomatic_mapdata_vessel)", row)
                                                    except:
                                                        print row
                                                        raise
                                            cur.execute("insert into appomatic_mapimport_downloaded (src, filename) values ('KSAT', %(filename)s)", {'filename': filename})

                                        except Exception, e:
                                            raise
                                            print "    Error loading file " + str(e)
                                            cur.execute("rollback")
                                        else:
                                            cur.execute("commit")

                                except Exception, e:
                                    raise
                                    print "    Unable to open file " + str(e)
