import django.core.management.base
import optparse
import contextlib
import django.db
import paramiko
import sys
import appomatic_mapimport.ksat
import appomatic_mapimport.mapimport
import datetime
import pytz
from django.conf import settings


class Command(appomatic_mapimport.mapimport.RowFilterEasterIsland, appomatic_mapimport.mapimport.SftpImport):
    help = 'Import data from exact earth'
    SRC = 'KSAT'

    def connectioninfo(self):
        return settings.MAPIMPORT_KSAT

    def sourcedirs(self):
        yield "WWW/AIS"

    def filepathsforname(self, sourcedir, filename):
        if filename.endswith('.nmea'):
            yield sourcedir + "/" + filename

    def loadfile(self, file):
        for row in appomatic_mapimport.ksat.convert(file):
            if 'C' in row:
                row['C'] = datetime.datetime.utcfromtimestamp(int(row['C'])).replace(tzinfo=pytz.utc)
            else:
                row['C'] = None
            if 'S' in row:
                row['S'] = 'KSAT-' + row['S']
            else:
                row['S'] = 'KSAT'
            #print row
            #print "    %(C)s: %(mmsi)s" % row
            row['hasposition'] = row.get('x', None) is not None

            if 'mmsi' in row: row['mmsi'] = str(row['mmsi'])

            row['SRC'] = row['S']
            row['datetime'] = row['C']
            row['latitude'] = row.get('y', None)
            row['longitude'] = row.get('x', None)
            row['length'] = row.get('dim_a', None)

            yield row
