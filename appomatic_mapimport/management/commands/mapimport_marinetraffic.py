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
import pytz
import StringIO
import lxml.etree
import traceback

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))

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

    urlpattern = "http://marinetraffic.com/ais/shipdetails.aspx?mmsi=%(mmsi)s"

    def handle2(self, *args, **options):
        with contextlib.closing(django.db.connection.cursor()) as cur:
            with contextlib.closing(django.db.connection.cursor()) as cur2:

                cur.execute("select distinct mmsi from appomatic_mapdata_ais where mmsi not in (select mmsi from appomatic_mapdata_vessel)");
                for ind, row in enumerate(dictreader(cur)):
                    print row['mmsi']
                    try:
                        h = httplib2.Http()
                        resp, content = h.request(self.urlpattern % row, "GET")
                        if not resp['status'] == '200':
                            print "BAD STATUS", resp['status']
                            continue
                        content = lxml.html.soupparser.fromstring(content)

                        data = {"title": content.xpath(".//div[@id='detailtext']/h1/text()[1]")[0]}

                        key = None
                        for child in content.xpath(".//div[@id='detailtext']/node()"):
                            tag = getattr(child, 'tag', None)
                            if tag == 'b':
                                key = child.text
                            elif tag is None and key is not None:
                                data[key] = unicode(child)
                            else:
                                key = None

                        # Example of data:
                        # {'Call Sign:': u' FAA6873',
                        #  'Speed/Course': u' 5.4 knots / 0\u02da',
                        #  'title': 'GREY PEARL',
                        #  'Speed recorded (Max / Average):': u' 5.3 / 5.3 knots',
                        #  'Info Received:': u' 2013-03-13 06:42 (27d,
                        #  8h 15min ago)',
                        #  'Length x Breadth:': u' 0 m X 0 m',
                        #  'Area:': u' Pacific South',
                        #  'IMO:': u' 0,
                        #  ',
                        #  'Latitude / Longitude:': u' ',
                        #  'Last Known Port:': u' ',
                        #  'Flag:': u' France [FR]\xa0',
                        #  'Ship Type:': u' Sailing Vessel',
                        #  'MMSI:': u' 227147250'}

                        row = {
                            'mmsi': row['mmsi'],
                            'name': data['title'],
                            'type': data.get('Ship Type:', ''),
                            'length': data.get('Length x Breadth:', '').split('m')[0].strip() or None
                            }

                        cur2.execute("insert into appomatic_mapdata_vessel (src, mmsi, name, type, length) select 'MARINETRAFFIC', %(mmsi)s, %(name)s, %(type)s, %(length)s where %(mmsi)s not in (select mmsi from appomatic_mapdata_vessel)", row)

                        if ind % 5 == 0:
                            cur2.execute("commit")
                    except Exception, e:
                        print e
                        #traceback.print_exc()
