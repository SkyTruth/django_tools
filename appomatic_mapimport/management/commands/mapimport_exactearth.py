import django.core.management.base
import optparse
import contextlib
import django.db
import paramiko
import sys
import appomatic_mapimport.ee
from django.conf import settings


class Command(django.core.management.base.BaseCommand):
    help = 'Import data from exact earth'

    def handle(self, *args, **options):
        with contextlib.closing(django.db.connection.cursor()) as cur:

            cur.execute("select filename from appomatic_mapimport_downloaded where src='EXACTEARTH'");
            oldfiles = set(row[0] for row in cur.fetchall())

            with contextlib.closing(paramiko.Transport((settings.MAPIMPORT_EXACTEARTH['host'], settings.MAPIMPORT_EXACTEARTH['port']))) as transport:
                transport.connect(username=settings.MAPIMPORT_EXACTEARTH['username'], password=settings.MAPIMPORT_EXACTEARTH['password'])
                with contextlib.closing(paramiko.SFTPClient.from_transport(transport)) as sftp:

                    for sourcedir in ("SAISData", "SAISData/old"):
                        for filename in sftp.listdir(sourcedir):
                            if filename.endswith('.complete'):

                                filename = filename[:-len(".complete")]
                                filepath = sourcedir + "/" + filename + ".csv"

                                if filename in oldfiles:
                                    print filepath + " (OLD)"
                                else:
                                    print filepath

                                    try:
                                        with contextlib.closing(sftp.file(filepath)) as file:

                                            cur.execute("begin")
                                            try:

                                                for row in appomatic_mapimport.ee.convert(file):
                                                    #print "    %(datetime)s: %(mmsi)s" % row
                                                    try:
                                                        cur.execute("insert into appomatic_mapdata_ais (src, datetime, mmsi, latitude, longitude, true_heading, sog, cog) values ('EXACTEARTH', %(datetime)s, %(mmsi)s, %(latitude)s, %(longitude)s, %(true_heading)s, %(sog)s, %(cog)s)", row)
                                                    except:
                                                        print row
                                                        raise
                                                    if row['name'] is not None and row['type'] is not None:
                                                        try:
                                                            cur.execute("insert into appomatic_mapdata_vessel (mmsi, name, type, length) select %(mmsi)s, %(name)s, %(type)s, %(length)s where %(mmsi)s not in (select mmsi from appomatic_mapdata_vessel)", row)
                                                        except:
                                                            print row
                                                            raise
                                                cur.execute("insert into appomatic_mapimport_downloaded (src, filename) values ('EXACTEARTH', %(filename)s)", {'filename': filename})

                                            except Exception, e:
                                                print "    Error loading file " + str(e)
                                                cur.execute("rollback")
                                            else:
                                                cur.execute("commit")

                                    except Exception, e:
                                        print "    Unable to open file " + str(e)
