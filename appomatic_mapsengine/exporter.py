import appomatic_mapsengine.models
import optparse
import contextlib
import datetime
import time
import sys
import os.path
import logging
import pytz
import urllib2
import httplib2
import geojson
import shapely.wkt
import fcdjangoutils.jsonview
import oauth2client.client
import django.db.transaction
import django.core.management.base
import csv
import fcdjangoutils.sqlutils
import StringIO
import fcdjangoutils.jsonview
from django.conf import settings 

RETRIES = 1
REQUEST_DELAY = 3

dbtovrtnames = {
    'BINARY': 'Binary',
    'BINARYARRAY': 'Binary',
    'BOOLEAN': 'String',
    'BOOLEANARRAY': 'String',
    'DATE': 'Date',
    'DATEARRAY': 'String',
    'DATETIME': 'DateTime',
    'DATETIMEARRAY': 'String',
    'DECIMAL': 'Real',
    'DECIMALARRAY': 'RealList',
    'FLOAT': 'Real',
    'FLOATARRAY': 'RealList',
    'INTEGER': 'Integer',
    'INTEGERARRAY': 'IntegerList',
    'INTERVAL': 'Real',
    'INTERVALARRAY': 'RealList',
    'PYDATE': 'DateTime',
    'PYDATEARRAY': 'String',
    'PYDATETIME': 'DateTime',
    'PYDATETIMEARRAY': 'String',
    'PYINTERVAL': 'Real',
    'PYINTERVALARRAY': 'RealList',
    'PYTIME': 'Time',
    'PYTIMEARRAY': 'String',
    'ROWID': 'Integer',
    'ROWIDARRAY': 'IntegerList',
    'STRING': 'String',
    'STRINGARRAY': 'StringList',
    'TIME': 'Time',
    'TIMEARRAY': 'String',
    'UNICODE': 'String',
    'UNICODEARRAY': 'String'
    }

pythontovrtnames = {
    'dict': 'String',
    'list': 'String',
    'tuple': 'String',
    'str': 'String',
    'unicode': 'String',
    'int': 'Integer',
    'float': 'Real',
    'bool': 'String',
    'NoneType': 'String',
}

colnames = {
    'the_geom': 'geom',
    'geom': 'geom',
    'gemoetry': 'geom',
    'location': 'geom',
    'lat': 'lat',
    'latitude': 'lat',
    'lon': 'lon',
    'lng': 'lon',
    'longitude': 'lon'
    }

class RequestException(Exception):
    def __init__(self, response, content, url, kw):
        self.response = response
        self.content = content
        self.url = url
        self.kw = kw
        Exception.__init__(self)
    def __unicode__(self):
        return "%s %s\n%s\n%s" % (self.response['status'], self.url, fcdjangoutils.jsonview.to_json(self.response, indent=2), fcdjangoutils.jsonview.to_json(self.content, indent=2))
    def __str__(self): return unicode(self).encode("utf-8")
    def __repr__(self): return unicode(self)

class Exporter(object):
    def log(self, **info):
        self.logstatus.update(info)
        if self.out:
            self.out.write(fcdjangoutils.jsonview.to_json(self.logstatus) + "\n")
            self.out.flush()
        else:
            print info["status"]

    def load_geom(self, geom):
        try:
            return fcdjangoutils.jsonview.from_json(geojson.dumps(shapely.wkt.loads(geom)))
        except:
            self.log(status="GEOM: %s\n" % (geom,))
            raise

    def request(self, url, as_json=True, raise_errors=True, retries=RETRIES, **kw):
        time.sleep(REQUEST_DELAY)
        while retries:
            retries -= 1
            kw['headers'] = dict(kw.get('headers', {}))
            if 'body' in kw and as_json:
                try:
                    kw['body'] = fcdjangoutils.jsonview.to_json(kw['body'])
                except:
                    import pdb
                    pdb.set_trace()
                kw['headers']["Content-Type"] = "application/json"
            response, content = self.http.request(url, **kw)
            try:
                content = fcdjangoutils.jsonview.from_json(content)
            except:
                pass
            response['status'] = int(response['status'])
            if response['status'] < 200 or response['status'] > 299:
                if retries:
                    self.log(status="retry")
                    continue
                elif raise_errors:
                    raise RequestException(response, content, url, kw)
            return response, content

    def connect(self):
        with file(settings.GOOGLE_MAPSENGINE_KEY, 'rb') as key_file:
            key = key_file.read()
        credentials = oauth2client.client.SignedJwtAssertionCredentials(
            settings.GOOGLE_MAPSENGINE_EMAIL, key, scope=settings.GOOGLE_MAPSENGINE_APIURL)
        self.http = httplib2.Http()
        self.http = credentials.authorize(self.http)


    # Flatten a column tree from json
    def addcols(self, cols, value, prefix):
        if isinstance(value, dict):
            for key, subvalue in value.iteritems():
                self.addcols(cols, subvalue, prefix + (key,))
        else:
            cols['__'.join(prefix)] = pythontovrtnames.get(type(value).__name__, "String")

    def addcolvalues(self, row, value, prefix):
        if isinstance(value, dict):
            for key, subvalue in value.iteritems():
                self.addcolvalues(row, subvalue, prefix + (key,))
        elif isinstance(value, (str, unicode, int, float, bool)) or value is None:
            row['__'.join(prefix)] = value
        else:
            row['__'.join(prefix)] = fcdjangoutils.jsonview.to_json(value)

    def flattencols(self, row):
        for key in row.keys():
            if key.endswith("_info"):
                self.addcolvalues(row, fcdjangoutils.jsonview.from_json(row.pop(key)), (key[:-len("_info")],))
        return row


    def __init__(self, queryset, out=None):
        self.start_time = datetime.datetime.now()

        self.out = out
        self.logstatus = {"done": 0}

        self.connect()

        with contextlib.closing(django.db.connection.cursor()) as cur:
            for export in queryset:
                self.log(status="Exporting %s\n" % (export,))
                
                lastid = export.lastid

                if export.projectid:
                    self.log(status="Getting column names and types\n")
                    cur.execute("select * from (" + export.query + ") as a limit 1")
                    row = fcdjangoutils.sqlutils.dictreader(cur).next()
                    dbmodule = sys.modules[type(cur.db.connection).__module__]
                    cols = {}

                    for col in cur.description:
                        if col.name.endswith("_info"):
                            self.addcols(cols, fcdjangoutils.jsonview.from_json(row[col.name]), (col.name[:-len("_info")],))
                        else:
                            cols[col.name] = "String"
                            for dbname, vrtname in dbtovrtnames.iteritems():
                                if col.type_code == getattr(dbmodule, dbname):
                                    cols[col.name] = vrtname
                                    break

                    geocols = {}
                    for colname, usage in colnames.iteritems():
                        if colname in cols:
                            geocols[usage] = colname

                    vrtinfo = {}
                    if 'geom' in geocols:
                        vrtinfo['geomtype'] = 'wkbUnknown'
                        vrtinfo['geofield'] = """<GeometryField encoding="WKT" reportSrcColumn="false" field="%(geom)s"/>"""  % geocols
                    elif 'lat' in geocols and 'lon' in geocols:
                        vrtinfo['geomtype'] = 'wkbPoint'
                        vrtinfo['geofield'] = """<GeometryField encoding="PointFromColumns" reportSrcColumn="false" x="%(lon)s" y="%(lat)s"/>"""  % geocols
                    else:
                        raise Exception("No geometry column found!")

                    vrtinfo['fields'] = '\n'.join(
                        """<Field name="%s" src="%s" type="%s"/>""" % (colname, colname, coltype)
                        for colname, coltype in cols.iteritems()
                        if colname not in (geocols.get('geom', None), geocols.get('lat', None), geocols.get('lon', None)))

                    vrt = """
                      <OGRVRTDataSource> 
                        <OGRVRTLayer name="file"> 
                          <SrcDataSource relativeToVrt="1">file.csv</SrcDataSource>
                          <GeometryType>%(geomtype)s</GeometryType> 
                          <LayerSRS>WGS84</LayerSRS>
                          %(geofield)s
                          %(fields)s
                        </OGRVRTLayer> 
                      </OGRVRTDataSource>
                    """ % vrtinfo

                    self.log(status="Loading data\n")
                    data_file = StringIO.StringIO()
                    data = csv.DictWriter(data_file, cols.keys(), extrasaction='ignore')
                    data.writeheader()
                    cur.execute("select * from (" + export.query + ") as a")

                    for row in fcdjangoutils.sqlutils.dictreader(cur):
                        data.writerow(self.flattencols(row))
                    data = data_file.getvalue()

                    info = {
                        "projectId": export.projectid,
                        "name": "%s-%s" % (export.slug, self.start_time.strftime("%Y-%m-%d-%H:%M:%S.%f")),
                        "description": "%s at %s" % (export.name, self.start_time.strftime("%Y-%m-%d %H:%M:%S.%f GMT%z")),
                        "files": [{"filename": "file.vrt"},
                                  {"filename": "file.csv"}],
                        "draftAccessList": export.access_list or "Map Editors",
                        "sourceEncoding": "UTF-8",
                        "tags": export.tags and [tag.strip() for tag in export.tags.split(",")] or []
                        }

                    self.log(status="Creating table\n")
                    response, content = self.request(
                            "https://www.googleapis.com/mapsengine/v1/tables/upload", method="POST", body=info)
                    tableid = content['id']

                    self.log(status="Uploading table schema\n")
                    response, content = self.request(
                        "https://www.googleapis.com/upload/mapsengine/v1/tables/%s/files?filename=file.vrt" % tableid,
                        method="POST",
                        as_json=False,
                        body = vrt)

                    self.log(status="Uploading table content\n")
                    response, content = self.request(
                        "https://www.googleapis.com/upload/mapsengine/v1/tables/%s/files?filename=file.csv" % tableid,
                        method="POST",
                        as_json=False,
                        body = data)


                elif export.tableid:
                    if export.clear:
                        self.log(status="Deleting old data\n")
                        while True:
                            where = ''
                            if export.keep_days != 0:
                                delete_before = datetime.date.today() - datetime.timedelta(export.keep_days)
                                delete_before = datetime.datetime(*delete_before.timetuple()[:3])
                                where = "where=" + urllib.quote('epoch<' + delete_before.strftime("%s"))

                            response, content = self.request(
                                "https://www.googleapis.com/mapsengine/v1/tables/%s/features?maxResults=50%s" % (export.tableid, where))
                            if not content['features']: break

                            response, content = self.request(
                                "https://www.googleapis.com/mapsengine/v1/tables/%s/features/batchDelete" % (export.tableid,),
                                method="POST",
                                body={"gx_ids":
                                          [feature['properties']['gx_id'] for feature in content['features']]})
                            self.log(status=".")
                            
                        lastid = -1

                    self.log(status="Clearing overshooting data\n")
                    while True:
                        response, content = self.request(
                            "https://www.googleapis.com/mapsengine/v1/tables/%s/features?maxResults=50&where=%s" % (export.tableid, urllib2.quote("id>%s" % lastid)))
                        if not content['features']: break

                        lastid = max([int(x['properties']['id']) for x in content['features']])
                        self.log(status="Cleared to %s\n" % lastid)
                else:
                    raise Exception("Neither tableid nor projectid specified...")

                while True:
                    cur.execute("select * from (" + export.query + ") as a where id > %(lastid)s order by id asc limit 50", {'lastid': lastid})
                    features = []
                    lastid = None
                    for row in fcdjangoutils.sqlutils.dictreader(cur):
                        geom = row.pop('the_geom')
                        if geom is None: continue
                        lastid = row['id']
                        row['gx_id'] = str(row['id'])
                        if 'info' in row:
                            row.update(fcdjangoutils.jsonview.from_json(row.pop('info')))
                        for key in row.keys():
                            if isinstance(row[key], int): row[key] = str(row[key])
                            if isinstance(row[key], datetime.datetime): row[key] = str(int(time.mktime(row[key].timetuple()) * 1000000))
                            if isinstance(row[key], datetime.timedelta): row[key] = str(int(row[key].days * 24 * 60 * 60 * 1000000 + row[key].seconds * 1000000 + row[key].microseconds))
                            if key in ('longitude', 'latitude', 'location', 'glocation', 'shape'):
                                del row[key]
                        features.append({
                                "type": "Feature",
                                "geometry": self.load_geom(geom),
                                "properties": row})
                    if not features: break
                    
                    self.log(status="Pushing batch %s (%s)\n" % (lastid, len(features)))
                    response, content = self.request(
                        "https://www.googleapis.com/mapsengine/v1/tables/%s/features/batchInsert" % export.tableid, method="POST", body = {"features": features})

                    cur.execute("update appomatic_mapsengine_export set lastid=%(lastid)s where id=%(id)s", {'lastid': lastid, "id": export.id})

                    cur.execute("commit")

                cur.execute("commit")
