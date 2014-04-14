import json
import datetime
import struct
import dateutil.parser
import StringIO
import django.db
import contextlib
import os.path
from django.conf import settings

limit = 1000

def manglevalue(value):
    if isinstance(value, datetime.datetime):
        return float(value.strftime("%s"))
    return value

def manglerow(row):
    return (manglevalue(value) for value in row)

def dictreader(cur):
    cols = None
    for row in cur:
        if cols is None:
            cols = [dsc[0] for dsc in cur.description]
        yield dict(zip(cols, manglerow(row)))


class Bbox(object):
    def __init__(self, lonmin=-180, latmin=-90, lonmax=180, latmax=90):
        self.latmin=latmin
        self.latmax=latmax
        self.lonmin=lonmin
        self.lonmax=lonmax
    def __repr__(self):
        # left,bottom,right,top - all according to openlayers :)

        def f(v):
            res = str(v)
            if res.endswith(".0"):
                res = res[:-2]
            return res
        return "%s,%s,%s,%s" % (f(self.lonmin), f(self.latmin), f(self.lonmax), f(self.latmax))
    def children(self):
        height = float(self.latmax-self.latmin)
        width = float(self.lonmax-self.lonmin)
        return [
            Bbox(self.latmin, self.latmin+height/2, self.lonmin, self.lonmin+width/2),
            Bbox(self.latmin+height/2, self.latmax, self.lonmin, self.lonmin+width/2),
            Bbox(self.latmin+height/2, self.latmax, self.lonmin+width/2, self.lonmax),
            Bbox(self.latmin, self.latmin+height/2, self.lonmin+width/2, self.lonmax)]
    def sql(self):
        return "latitude >= %s and latitude < %s and longitude >= %s and longitude < %s" % (self.latmin, self.latmax, self.lonmin, self.lonmax)


def timestamp(data):
    return int(dateutil.parser.parse(data).strftime("%s"))

def conv(data, t, default):
    try:
        return t(data)
    except:
        return default

typemap = {
    timestamp: 'Int32',
    int: 'Int32',
    float: 'Float32',
    }

typeformatmap = {
    'Int32': 'i',
    'Float32': 'f'
    }
typedefaultmap = {
    'Int32': 0,
    'Float32': 0.0
    }



def index(request, bbox):
    filename = os.path.join(settings.MEDIA_ROOT, "tiles", bbox)
    if not os.path.exists(filename):
        with contextlib.closing(django.db.connection.cursor()) as cur:
            bbox = Bbox(*[float(item) for item in bbox.split(",")])

            cur.execute("""
                select *
                from
                  (select *
                   from tiledata
                   where %s
                   order by rnd limit %s) y
                order by datetime asc
                """ % (bbox.sql(), limit))
            data = [row for row in dictreader(cur)]

            header = {}
            datalen = len(data)
            cols = {}
            coltypes = {}
            nrseries = 0;
            series = lambda : 1 # Not equal to anything that you can find in a json
            for i, d in enumerate(data):
                if d.get('series', None) != series:
                    nrseries += 1;
                    series = d.get('series', None)
                for key, value in d.iteritems():
                    if value == '__None__' or value is None: continue
                    t = type(value)
                    if t is str or t is unicode:
                        # If it's clearly not a date, avoid the time to throw and exception...
                        if not value or value[0] not in '0123456789': continue
                        try:
                            value = timestamp(value)
                            t = timestamp
                        except:
                            continue
                    if key not in cols:
                        cols[key] = {'name': key, 'type': typemap[t], 'min': value, 'max': value}
                        coltypes[key] = t
                    cols[key]['max'] = max(cols[key]['max'], value)
                    cols[key]['min'] = min(cols[key]['min'], value)
                if i % 1000 == 0:
                    print "%.2f%%" % (100 * float(i) / datalen)

            cols = cols.values()
            cols.sort(lambda a, b: cmp(a['name'], b['name']))
            header.update({'cols': cols, 'length': len(data), 'series': nrseries})
            headerstr = json.dumps(header)

            with open(filename, "w") as f:
                f.write(struct.pack("<i", len(headerstr)))
                f.write(headerstr)

                formatmap = '<' + ''.join(typeformatmap[col['type']] for col in cols)
                colspecs = [{'name': col['name'], 'type': coltypes[col['name']], 'default': typedefaultmap[col['type']]} for col in cols]

                for d in data:
                    f.write(struct.pack(
                            formatmap,
                            *[conv(d[colspec['name']], colspec['type'], colspec['default'])
                              for colspec in colspecs]))

    with open(filename) as f:
        res = django.http.HttpResponse(f.read(), mimetype="application/binary")
        res["Access-Control-Allow-Origin"] = "*"
        return res
