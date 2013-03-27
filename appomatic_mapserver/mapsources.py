import appomatic_mapdata.models
import datetime
import django.db
import math

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))

class MapSource(object):
    implementations = {}

    def __new__(cls, layer, urlquery, *arg, **kw):
        if cls is MapSource:
            return cls.implementations[layer.layerdef.backend_type](layer, urlquery, *arg, **kw)
        else:
            return object.__new__(cls, layer, urlquery, *arg, **kw)

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            module = members.get('__module__', '__main__')
            if name != "MapSource" or module != "appomatic_mapserver.mapsources":
                MapSource.implementations[module + "." + name] = cls

    def __init__(self, layer, urlquery):
        self.layer = layer
        self.urlquery = urlquery

    def __enter__(self):
        self.cur = django.db.connection.cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.cur.close()

    def get_query(self):
        datetimemin = int(self.urlquery['datetime__gte'])
        datetimemax = int(self.urlquery['datetime__lte'])
        lon1,lat1,lon2,lat2 = [float(coord) for coord in self.urlquery['bbox'].split(",")]
        return {
            "timeminstamp": datetimemin,
            "timemaxstamp": datetimemax,
            "timemin": datetime.datetime.utcfromtimestamp(datetimemin),
            "timemax": datetime.datetime.utcfromtimestamp(datetimemax),
            "lonmin": min(lon1, lon2),
            "latmin": min(lat1, lat2),
            "lonmax": max(lon1, lon2),
            "latmax": max(lat1, lat2)
            }

    def get_table(self):
        return self.layer.layerdef.query

    def get_bboxsql(self):
        bboxmin = "ST_Point(%(lonmin)s, %(latmin)s)"
        bboxmax = "ST_Point(%(lonmax)s, %(latmax)s)"
        bbox = "st_setsrid(ST_MakeBox2D(" + bboxmin + ", " + bboxmax + "), (4326))"
        bboxdiag = "ST_Distance(" + bboxmin + ", " + bboxmax + ")"
        return {
            "bboxmin": bboxmin,
            "bboxmax": bboxmax,
            "bbox": bbox,
            "bboxdiag": bboxdiag
            }

    def get_map_data(self):
        for row in self.get_map_data_raw():
            if row.get('mmsi', None):
                if not row.get('name', None):
                    row['name'] = row['mmsi']
                if not row.get('url', None):
                    row['url'] = appomatic_mapdata.models.Ais.URL_PATTERN % row

                row['itu_url'] = appomatic_mapdata.models.Ais.URL_PATTERN_ITU % row

            if not row.get('mmsi', None):
                row['mmsi'] = ''
            if not row.get('name', None):
                row['name'] = ''
            if not row.get('url', None):
                row['url'] = ''
            if not row.get('type', None):
                row['type'] = ''
            if not row.get('length', None):
                row['length'] = ''


            yield row

class TolerancePathMap(MapSource):
    name = 'Simplified path'
    def get_tolerance(self):
        query = self.get_query()
        bboxsql = self.get_bboxsql()

        if self.urlquery.get('full', 'false') == 'true':
            return None
        else:
            self.cur.execute("select " + bboxsql['bboxdiag'] + " / 100", query)
            tolerance = self.cur.fetchone()[0]

            # Round to nearest (lower) 2^x as those are the only tolerances implemented in the view...
            # Fixme: Handle min and max...
            return 2**int(math.log(float(tolerance), 2))

    def get_map_data_raw(self):
        query = self.get_query()
        bboxsql = self.get_bboxsql()

        query['tolerance'] = self.get_tolerance()

        tolerancetest = "tolerance = %(tolerance)s"
        if query['tolerance'] is None:
            tolerancetest = "tolerance is null"

        sql = """
          select
            mmsi,
            ST_AsText(shape) as shape,
            extract(epoch from timemin) as datetime,
            timemin,
            timemax,
            name,
            type,
            length
          from
            (select
               ais_path.mmsi,
               ST_Intersection(
                 ST_locate_between_measures(
                   line,
                   extract(epoch from %(timemin)s::timestamp),
                   extract(epoch from %(timemax)s::timestamp)
                 ),
                 """ + bboxsql['bbox'] + """) as shape,
               timemin,
               timemax,
                vessel.name,
               vessel.type,
               vessel.length
             from
               """ + self.get_table() + """ as ais_path
               left outer join appomatic_mapdata_vessel as vessel on
                 ais_path.mmsi = vessel.mmsi
             where
               """ + tolerancetest + """
               and not (%(timemax)s < timemin or %(timemin)s > timemax)
               and ST_Intersects(
                 line,
                 """ + bboxsql['bbox'] + """)) as a
          where
            not ST_IsEmpty(shape)
        """

        self.cur.execute(sql, query)
        try:
            for row in dictreader(self.cur):
                yield row
        finally:
            print "TOLERANCE:", query['tolerance']
            print "RESULTS: ", self.cur.rowcount


    def get_timeframe(self):
        self.cur.execute("select min(timemin), max(timemax) from " + self.get_table() + " as a")
        row = self.cur.fetchone()
        return {'timemin': int(row[0].strftime('%s')), 'timemax': int(row[1].strftime("%s"))}


class EventMap(MapSource):
    name = 'Event list'
    def get_map_data_raw(self):
        query = self.get_query()
        bboxsql = self.get_bboxsql()

        sql = """
          select
            *,
            extract(epoch from datetime) as datetime,
            ST_AsText(location) as shape
          from
            """ + self.get_table() + """ as a
          where
            not (%(timemax)s < datetime or %(timemin)s > datetime)
            and ST_Contains(
              """ + bboxsql['bbox'] + """, location)
          order by
            a.datetime desc
        """

        if 'limit' in self.urlquery:
            sql += "limit %(limit)s"
            query['limit'] = self.urlquery['limit']

        self.cur.execute(sql, query)
        try:
            for row in dictreader(self.cur):
                yield row
        finally:
            print "RESULTS: ", self.cur.rowcount

    def get_timeframe(self):
        self.cur.execute("select min(datetime), max(datetime) from " + self.get_table() + " as a")
        row = self.cur.fetchone()
        return {'timemin': int(row[0].strftime('%s')), 'timemax': int(row[1].strftime("%s"))}
