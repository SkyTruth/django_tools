import json
import datetime
import struct
import dateutil.parser
import StringIO
import django.db
import contextlib
import os.path
import fcdjangoutils.cors
import fcdjangoutils.jsonview
import appomatic_tileserver.models
import django.views.decorators.csrf
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
    if not isinstance(data, datetime.datetime):
        data = dateutil.parser.parse(data)
    return int(data.strftime("%s"))

def conv(data, t, default):
    try:
        return t(data)
    except:
        return default

typemap = {
    datetime: 'Int32',
    int: 'Int32',
    float: 'Float32',
    bool: 'Int32'
    }

typeconvertmap = {
    datetime: timestamp,
    int: int,
    float: float,
    bool: bool
}

typeformatmap = {
    'Int32': 'i',
    'Float32': 'f'
    }
typedefaultmap = {
    'Int32': 0,
    'Float32': 0.0
    }

def is_tileset_lines(tileset):
    with contextlib.closing(django.db.connection.cursor()) as cur:
        cur.execute("select * from %(tileset)s limit 1" % {"tileset": tileset})
        for row in dictreader(cur):
            return 'series' in row

def get_data_plain(tileset, bbox):
    with contextlib.closing(django.db.connection.cursor()) as cur:
        cur.execute("""
          select *
          from
            (select *
             from %(tileset)s
             where %(bbox)s
             order by rnd limit %(limit)s) y
          order by datetime asc
        """ % {"tileset":tileset, "bbox":bbox.sql(), "limit": limit})
        return [row for row in dictreader(cur)]

def get_data_series(tileset, bbox):
    with contextlib.closing(django.db.connection.cursor()) as cur:
        cur.execute("""
          select
            *
          from
            (
              (
                select
                  *,
                  false as virtual
                from
                  %(tileset)s
                where
                  %(bbox)s
                order by
                  rnd
                limit %(limit)s
              ) union (
                select
                  distinct on (res.series)
                  res.*,
                  true as virtual
                from
                  (
                    select
                      series,
                      min(datetime) min,
                      max(datetime) max
                    from
                      %(tileset)s
                    where
                      %(bbox)s
                    group by series
                  ) minmax
                  join %(tileset)s res on
                    res.series = minmax.series
                    and res.datetime < minmax.min
                order by
                  res.series, res.datetime desc
              ) union (
                select
                  distinct on (res.series)
                  res.*,
                  true as virtual
                from
                  (
                    select
                      series,
                      min(datetime) min,
                      max(datetime) max
                    from
                      %(tileset)s
                    where
                      %(bbox)s
                    group by series
                  ) minmax
                  join %(tileset)s res on
                    res.series = minmax.series
                    and res.datetime > minmax.max
                order by
                  res.series, res.datetime asc
              )
            ) a
          order by
            series, datetime asc
        """ % {"tileset":tileset, "bbox":bbox.sql(), "limit": limit})
        return [row for row in dictreader(cur)]

@django.views.decorators.csrf.csrf_exempt
@fcdjangoutils.cors.cors(headers = ['Origin', 'X-Requested-With', 'Content-Type', 'Accept', 'X-Client-Cache'])
@fcdjangoutils.jsonview.json_view
def series(request, tileset):
    body = json.loads(request.body)

    return {
        "IMO": "-",
        "MMSI": body['series'],
        "Call Sign": "SKHD",
        "Flag": "Sweden (SE)",
        "AIS Type": "Special Craft",
        "Gross Tonnage": "-",
        "DeadWeight": "-",
        "Length x Breadth": "17m x 5m",
        "Year Built": "-",
        "Status": "Active",
        "name": "Flying Dutchman",
        "link": "http://www.marinetraffic.com/en/ais/details/ships/265511380/vessel:PILOT_746_SE"
        }

@fcdjangoutils.cors.cors(headers = ['Origin', 'X-Requested-With', 'Content-Type', 'Accept', 'X-Client-Cache'])
def index(request, tileset, bbox):
    pathname = os.path.join(settings.MEDIA_ROOT, "tiles", tileset)
    filename = os.path.join(pathname, bbox)
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    if not os.path.exists(filename):
        bbox = Bbox(*[float(item) for item in bbox.split(",")])

        if is_tileset_lines(tileset):
            print "Tileset '%s' is lines" % tileset
            data = get_data_series(tileset, bbox)
        else:
            print "Tileset '%s' is points" % tileset
            data = get_data_plain(tileset, bbox)

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
                if t not in typemap: continue
                if key not in cols:
                    cols[key] = {'name': key, 'type': typemap[t], 'min': value, 'max': value}
                    coltypes[key] = t
                cols[key]['max'] = max(cols[key]['max'], value)
                cols[key]['min'] = min(cols[key]['min'], value)
            if i % 1000 == 0:
                print "%.2f%%" % (100 * float(i) / datalen)

        if 'datetime' in cols: cols['datetime']['multiplier'] = 1000
        if 'red' in cols: cols['red']['multiplier'] = 1.0/256
        if 'green' in cols: cols['green']['multiplier'] = 1.0/256
        if 'blue' in cols: cols['blue']['multiplier'] = 1.0/256
        if 'magnitude' in cols: cols['magnitude']['multiplier'] = 1.0/256

        cols = cols.values()
        cols.sort(lambda a, b: cmp(a['name'], b['name']))
        header.update({'cols': cols, 'length': len(data), 'series': nrseries})
        headerstr = json.dumps(header)

        print headerstr

        with open(filename, "w") as f:
            f.write(struct.pack("<i", len(headerstr)))
            f.write(headerstr)

            formatmap = '<' + ''.join(typeformatmap[col['type']] for col in cols)
            colspecs = [{'name': col['name'], 'conv': typeconvertmap[coltypes[col['name']]], 'default': typedefaultmap[col['type']]} for col in cols]

            for d in data:
                f.write(struct.pack(
                        formatmap,
                        *[conv(d[colspec['name']], colspec['conv'], colspec['default'])
                          for colspec in colspecs]))

    with open(filename) as f:
        res = django.http.HttpResponse(f.read(), mimetype="application/binary")
        res["Access-Control-Allow-Origin"] = "*"
        return res

@django.views.decorators.csrf.csrf_exempt
@fcdjangoutils.cors.cors(headers = ['Origin', 'X-Requested-With', 'Content-Type', 'Accept', 'X-Client-Cache'])
@fcdjangoutils.jsonview.json_view
def workspace(request):
    if request.method == "POST":
        workspace = appomatic_tileserver.models.Workspace(definition = request.body)
        workspace.save()
        return {"id": workspace.id}
    else:
        return json.loads(appomatic_tileserver.models.Workspace.objects.get(id=request.GET['id']).definition)

@django.views.decorators.csrf.csrf_exempt
@fcdjangoutils.cors.cors(headers = ['Origin', 'X-Requested-With', 'Content-Type', 'Accept', 'X-Client-Cache'])
@fcdjangoutils.jsonview.json_view
def log(request):
    if request.method == "POST":
        appomatic_tileserver.models.Log(data = request.body).save()
        return {}
