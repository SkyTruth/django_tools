import appomatic_mapsengine.models
import optparse
import contextlib
import datetime
import time
import sys
import os.path
import logging
import pytz
import json
import urllib2
import httplib2
import geojson
import shapely.wkt
import fcdjangoutils.jsonview
import oauth2client.client
import django.db.transaction
import django.core.management.base
from django.conf import settings 

def dictreader(cur):
    cols = None
    for row in cur:
        if cols is None: cols = [x[0] for x in cur.description]
        yield dict(zip(cols, row))


class RequestException(Exception):
    def __init__(self, response, content, url, kw):
        self.response = response
        self.content = content
        self.url = url
        self.kw = kw
        Exception.__init__(self)
    def __unicode__(self):
        return "%s %s\n%s\n%s" % (self.response['status'], self.url, json.dumps(self.response, indent=2), json.dumps(self.content, indent=2))
    def __str__(self): return unicode(self).encode("utf-8")
    def __repr__(self): return unicode(self)

class Exporter(object):
    def log(self, **info):
        if self.out:
            self.out.write(json.dumps(info) + "\n")
            self.out.flush()
        else:
            print info["status"]

    def load_geom(self, geom):
        try:
            return json.loads(geojson.dumps(shapely.wkt.loads(geom)))
        except:
            self.log(status="GEOM: %s\n" % (geom,))
            raise

    def request(self, url, raise_errors=True, **kw):
        time.sleep(1)
        kw['headers'] = dict(kw.get('headers', {}))
        if 'body' in kw:
            kw['body'] = json.dumps(kw['body'])
            kw['headers']["Content-Type"] = "application/json"
        response, content = self.http.request(url, **kw)
        try:
            content = json.loads(content)
        except:
            pass
        response['status'] = int(response['status'])
        if raise_errors:
            if response['status'] < 200 or response['status'] > 299:
                raise RequestException(response, content, url, kw)
        return response, content

    def connect(self):
        with file(settings.GOOGLE_MAPSENGINE_KEY, 'rb') as key_file:
            key = key_file.read()
        credentials = oauth2client.client.SignedJwtAssertionCredentials(
            settings.GOOGLE_MAPSENGINE_EMAIL, key, scope=settings.GOOGLE_MAPSENGINE_APIURL)
        self.http = httplib2.Http()
        self.http = credentials.authorize(self.http)


    def __init__(self, queryset, out=None):
        self.out = out

        self.connect()

        with contextlib.closing(django.db.connection.cursor()) as cur:
            for export in queryset:
                self.log(status="Exporting %s\n" % (export,))
                
                lastid = export.lastid

                if export.clear:
                    self.log(status="Deleteeting old data\n")
                    while True:
                        response, content = self.request(
                            "https://www.googleapis.com/mapsengine/v1/tables/%s/features?maxResults=50" % (export.tableid,))
                        if not content['features']: break

                        response, content = self.request(
                            "https://www.googleapis.com/mapsengine/v1/tables/%s/features/batchDelete" % (export.tableid,),
                            method="POST",
                            body={"gx_ids":
                                      [feature['properties']['gx_id'] for feature in content['features']]})
                    lastid = -1
                else:
                    self.log(status="Clearing overshooting data\n")
                    while True:
                        response, content = self.request(
                            "https://www.googleapis.com/mapsengine/v1/tables/%s/features?maxResults=50&where=%s" % (export.tableid, urllib2.quote("id>%s" % lastid)))
                        if not content['features']: break

                        lastid = max([int(x['properties']['id']) for x in content['features']])
                        self.log(status="Cleared to %s\n" % lastid)

                while True:
                    cur.execute("select * from (" + export.query + ") as a where id > %(lastid)s order by id asc limit 50", {'lastid': lastid})
                    features = []
                    lastid = None
                    for row in dictreader(cur):
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
                    
                    self.log(status="Pushing batch %s\n" % lastid)
                    response, content = self.request(
                        "https://www.googleapis.com/mapsengine/v1/tables/%s/features/batchInsert" % export.tableid, method="POST", body = {"features": features})

                    cur.execute("update appomatic_mapsengine_export set lastid=%(lastid)s where id=%(id)s", {'lastid': lastid, "id": export.id})

                    cur.execute("commit")

                    time.sleep(5)

                cur.execute("commit")
