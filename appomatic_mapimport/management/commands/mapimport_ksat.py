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


class Command(appomatic_mapimport.mapimport.SftpImport):
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

            # Why doesn't gpsdecode do scaling???
            if 'speed' in row:
                if row['speed'] >= 1023:
                    row['speed'] = None
                else:
                    row['speed'] = row['speed'] / 10.0 # A AIS speed unit is 1/10 of a knot
            if 'heading' in row: row['heading'] = row['heading'] / 10.0 # A AIS cog unit is 1/10 of a degree
            if 'course' in row: row['course'] = row['course'] / 10.0 # A AIS cog unit is 1/10 of a degree
            if 'lon' in row: row['lon'] = row['lon'] / 600000.0 # A AIS unit is 1/10000th of a minute (1/60th of a degree)
            if 'lat' in row: row['lat'] = row['lat'] / 600000.0
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
            row['hasposition'] = row.get('type', None) in (1, 2, 3)

            if 'mmsi' in row: row['mmsi'] = str(row['mmsi'])

            row['SRC'] = row['S']
            row['datetime'] = row['C']
            row['latitude'] = row.get('lat', None)
            row['longitude'] = row.get('lon', None)
            row['sog'] = row.get('speed', None)
            row['cog'] = row.get('course', None)
            row['true_heading'] = row.get('heading', None)

            row['name'] = row.get('shipname', None)
            row['type'] = row.get('shiptype', None)
            row['length'] = row.get('to_bow', None)

            yield row
