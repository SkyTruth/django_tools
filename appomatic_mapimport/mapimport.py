import django.core.management.base
import optparse
import contextlib
import django.db
import paramiko
import sys
import os.path
import appomatic_mapimport.ee
from django.conf import settings 
import datetime


class Import(django.core.management.base.BaseCommand):
    SRC = NotImplemented

    help = 'Import data'

    def connectioninfo(self):
        raise NotImplementedError

    @contextlib.contextmanager
    def connect(self):
        raise NotImplementedError

    def sourcedirs(self):
        raise NotImplementedError

    def filepathsforname(self, sourcedir, filename):
        yield sourcedir + "/" + filename

    def listfiles(self):
        raise NotImplementedError

    def download(self, filepath):
        raise NotImplementedError

    def filename(self, filepath):
        return os.path.split(filepath)[-1]

    def localpath(self, filepath):
        return os.path.join(self.dstdir, self.filename(filepath))

    def loadfile(self, file):
        raise NotImplementedError

    def insertrow(self, row):
        if row.get("hasposition", True):
            row['quality'] = row.get('quality', 1)
            self.cur.execute("insert into appomatic_mapdata_ais (src, srcfile, datetime, mmsi, latitude, longitude, true_heading, sog, cog, quality) values (%(SRC)s, %(filename)s, %(datetime)s, %(mmsi)s, %(latitude)s, %(longitude)s, %(true_heading)s, %(sog)s, %(cog)s, %(quality)s)", row)
        self.insert_row_vessel(row)

    def insert_row_vessel(self, row):
        if row.get('name', None) is not None:
            row['type'] = row.get('type', None)
            self.cur.execute("insert into appomatic_mapdata_vessel (src, srcfile, mmsi, name, type, length) select %(SRC)s, %(filename)s, %(mmsi)s, %(name)s, %(type)s, %(length)s where %(mmsi)s not in (select mmsi from appomatic_mapdata_vessel)", row)

    def handle(self, *args, **kwargs):
        try:
            return self.handle2(*args, **kwargs)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()

    def handle2(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.dstdir = os.path.join(settings.MEDIA_ROOT, 'mapimport', self.SRC)
        if not os.path.exists(self.dstdir):
            os.makedirs(self.dstdir)

        with contextlib.closing(django.db.connection.cursor()) as cur:
            self.cur = cur

            self.cur.execute("select filename from appomatic_mapimport_downloaded where src=%(SRC)s", {"SRC": self.SRC});
            self.oldfiles = set(row[0] for row in self.cur.fetchall())

            with self.connect():
                for filepath in self.listfiles():
                    filename = self.filename(filepath)

                    if filename in self.oldfiles:
                        print filepath + " (OLD)"
                    else:
                        print filepath

                        try:
                            self.download(filepath)
                            with open(self.localpath(filepath)) as file:
                                self.cur.execute("begin")
                                try:
                                    for row in self.loadfile(file):
                                        #print "    %(datetime)s: %(mmsi)s" % row
                                        if 'filename' not in row: row['filename'] = filename
                                        if 'SRC' not in row: row['SRC'] = self.SRC
                                        try:
                                            self.insertrow(row)
                                        except:
                                            print row
                                            raise

                                    self.cur.execute("insert into appomatic_mapimport_downloaded (src, filename, datetime) values (%(SRC)s, %(filename)s, %(datetime)s)", {'SRC': self.SRC, 'filename': filename, 'datetime': datetime.datetime.now()})

                                except Exception, e:
                                    print "    Error loading file " + str(e)
                                    import traceback
                                    traceback.print_exc()
                                    self.cur.execute("rollback")
                                else:
                                    self.cur.execute("commit")

                        except Exception, e:
                            print "    Unable to open file " + str(e)

class SftpImport(Import):
    help = 'Import data from sftp'

    @contextlib.contextmanager
    def connect(self):
        info = self.connectioninfo()
        with contextlib.closing(paramiko.Transport((info['host'], info['port']))) as transport:
            transport.connect(username=info['username'], password=info['password'])
            with contextlib.closing(paramiko.SFTPClient.from_transport(transport)) as sftp:
                self.connection = sftp
                yield

    def listfiles(self):
        for sourcedir in self.sourcedirs():
            for filename in self.connection.listdir(sourcedir):
                for filepath in self.filepathsforname(sourcedir, filename):
                    yield filepath

    def download(self, filepath):
        self.connection.get(filepath, self.localpath(filepath))
