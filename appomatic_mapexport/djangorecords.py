import django.db
import contextlib
import datetime
import appomatic_mapdata.models

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))

def get_records(**args):
    with contextlib.closing(django.db.connection.cursor()) as cur:
        if args.get('datetime__gte', None):
            args['timemin'] = datetime.datetime.utcfromtimestamp(int(args['datetime__gte']))
        if args.get('datetime__lte', None):
            args['timemax'] = datetime.datetime.utcfromtimestamp(int(args['datetime__lte']))
        if args.get('bbox', None):
            lon1,lat1,lon2,lat2 = [float(coord) for coord in args['bbox'].split(",")]
            args['lonmin'] = min(lon1, lon2)
            args['lonmax'] = max(lon1, lon2)
            args['latmin'] = min(lat1, lat2)
            args['latmax'] = max(lat1, lat2)

        where = ['true']
        if args.get('timemax', None):
            where.append("datetime <= %(timemax)s")
        if args.get('timemin', None):
            where.append("datetime >= %(timemin)s")
        if args.get('latmax', None):
            where.append("latitude <= %(latmax)s")
        if args.get('latmin', None):
            where.append("latitude >= %(latmin)s")
        if args.get('lonmax', None):
            where.append("longitude <= %(lonmax)s")
        if args.get('lonmin', None):
            where.append("longitude >= %(lonmin)s")
        if args.get('mmsi', None):
            where.append("ais.mmsi = %(mmsi)s")
        
        sql = """
          select
            ais.src as src,
            ais.srcfile as srcfile,
            ais.mmsi as mmsi,
            datetime,
            latitude,
            longitude,
            true_heading,
            sog,
            cog,
            location,
            name,
            type,
            length
          from
            appomatic_mapdata_ais as ais
            left join appomatic_mapdata_vessel as vessel on
              ais.mmsi = vessel.mmsi
          where
            """ + " and ".join(where) + """
          order by
            ais.mmsi,
            datetime
        """

        cur.execute(sql, args);
            
        for row in dictreader(cur):
            row['url'] = appomatic_mapdata.models.Ais.URL_PATTERN % row
            yield row
