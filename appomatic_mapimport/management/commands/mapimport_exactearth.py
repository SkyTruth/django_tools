import django.core.management.base
import optparse
import contextlib
import django.db
import paramiko
import sys
import appomatic_mapimport.ee
import appomatic_mapimport.mapimport
from django.conf import settings


class Command(appomatic_mapimport.mapimport.RowFilterEasterIsland, appomatic_mapimport.mapimport.SftpImport):
    SRC = 'EXACTEARTH'

    help = 'Import data from exact earth'

    def connectioninfo(self):
        return settings.MAPIMPORT_EXACTEARTH

    def sourcedirs(self):
        yield "SAISData"
        yield "SAISData/old"

    def filepathsforname(self, sourcedir, filename):
         if filename.endswith('.complete'):
             yield sourcedir + "/" + filename[:-len(".complete")] + ".csv"

    def loadfile(self, file):
        return appomatic_mapimport.ee.convert(file)
