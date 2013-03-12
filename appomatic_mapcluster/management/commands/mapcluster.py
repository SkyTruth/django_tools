import django.db
import django.core.management.base
import appomatic_mapdata.models
import optparse
import contextlib
import shapely.wkb
import shapely.wkt
import fastkml.kml
import fastkml.styles
import psycopg2
import optparse
import datetime

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))


class Command(django.core.management.base.BaseCommand):
    help = 'Calculates and exports clusters of events'
    args = '<query> <filename>'

    option_list = django.core.management.base.BaseCommand.option_list + (
        optparse.make_option('--size',
            action='store',
            dest='size',
            default=4,
            help='Minimum cluster size for a cluster to be included.'),
        optparse.make_option('--period',
            action='append',
            dest='periods',
            default=[],
            help='Time period to cluster over, start and end dates separated by a colon, e.g. 2013-01-01:2013-02-01. This option can be given multiple times to give multiple date ranges.'),
        )

    def extract_clusters(self, query, size, timeperiod, doc):
        if timeperiod is None:
            color = "ff00ffff"
        else:
            mincolor = (255, 00, 255, 00)
            maxcolor = (255, 00, 00, 255)
             # Min time: 1 month, max time, 1 year
            div = ((timeperiod[1] - timeperiod[0]).days-30) / (11*30.0)
            if div < 0.0: div = 0.0
            if div > 1.0: div = 1.0
            color = "%02x%02x%02x%02x" % tuple(c[1]*div + c[0]*(1.0-div)
                                               for c in zip(mincolor, maxcolor))

        self.cur.execute("""
          select
            *
          from
            """ + query + """ as a
          limit 1
        """)

        columns = dict((column.name, 
          (name
           for name, t in ((name, getattr(psycopg2, name))
                           for name in ("Date",
                                        "Time",
                                        "Timestamp",
                                        "DateFromTicks",
                                        "TimeFromTicks",
                                        "TimestampFromTicks",
                                        "Binary",
                                        "STRING",
                                        "BINARY",
                                        "NUMBER",
                                        "DATETIME",
                                        "ROWID"))
           if column.type_code == t).next())
         for column in self.cur.description)

        # Remove old data if any
        self.cur.execute("truncate table appomatic_mapcluster_cluster")

        #### Select the area and timeframe to work with, set SRID (to Albers Conic Equal Area - Florida NAD83) and store in cluster table
        filter = "true"
        args = {"period_min":timeperiod[0], "period_max":timeperiod[1]}
        if timeperiod is not None:
            filter = """
              datetime >= %(period_min)s and datetime <= %(period_max)s 
            """
            args["timeperiod"] = timeperiod
        self.cur.execute("""
          insert into appomatic_mapcluster_cluster (
            reportnum, src, datetime, latitude, longitude, location, glocation)
          select
            id,
            src,
            datetime,
            latitude,
            longitude,
            location,
            location
          from
            """ + query + """ as a
          where
            """ + filter, args)

        # Create buffer
        # self.cur.execute("update appomatic_mapcluster_cluster set buffer = st_buffer(location, 7500)")

        ### Compute score - all reports in buffer 
        ### Tack on the reportnum after the decimal place on the score
        ### so no two clusters will ever have the exact same score.
        ### This ensures that we don't get two overlapping clusters
        ### (with the same score, which would lead both of them to be
        ### included in the output)
        self.cur.execute("""
          update
            appomatic_mapcluster_cluster a
          set
            score = ((select
                        count(*) as c
                      from
                        appomatic_mapcluster_cluster b
                      where
                        ST_DWithin(a.glocation, b.glocation, 7500))
                     || '.' || reportnum)::double precision
        """)

        ### Set max_score equal to the highest score in the buffer 
        self.cur.execute("""
          update
            appomatic_mapcluster_cluster a
          set
             max_score = (select
                            max(score) as c
                          from
                            appomatic_mapcluster_cluster b
                          where
                            ST_DWithin(a.glocation, b.glocation, 7500))
        """)


        sqlcols = ["a.id",
                   "a.max_score::integer as count",
                   "ST_Y(ST_Centroid(ST_Collect(b.location))) as lat",
                   "ST_X(ST_Centroid(ST_Collect(b.location))) as lng",
                   "ST_AsText(ST_Centroid(ST_Collect(b.location))) as shape"]
        description = []
        for name, t in columns.iteritems():
            if t == "NUMBER":
                sqlcols.append("min(c.%s) as %s_min" % (name, name))
                sqlcols.append("max(c.%s) as %s_max" % (name, name))
                sqlcols.append("avg(c.%s) as %s_avg" % (name, name))
                sqlcols.append("stddev(c.%s) as %s_stddev" % (name, name))
                description.append("<tr><th>%s (min)</th><td>%%(%s_min)s" % (name, name))
                description.append("<tr><th>%s (max)</th><td>%%(%s_max)s" % (name, name))
                description.append("<tr><th>%s (avg)</th><td>%%(%s_avg)s" % (name, name))
                description.append("<tr><th>%s (stddev)</th><td>%%(%s_stddev)s" % (name, name))
            elif t == "DATETIME":
                sqlcols.append("min(c.%s) as %s_min" % (name, name))
                sqlcols.append("max(c.%s) as %s_max" % (name, name))
                sqlcols.append("to_timestamp(avg(extract('epoch' from c.%s))) as %s_avg" % (name, name))
                sqlcols.append("stddev(extract('epoch' from c.%s)) * interval '1second' as %s_stddev" % (name, name))
                description.append("<tr><th>%s (min)</th><td>%%(%s_min)s" % (name, name))
                description.append("<tr><th>%s (max)</th><td>%%(%s_max)s" % (name, name))
                description.append("<tr><th>%s (avg)</th><td>%%(%s_avg)s" % (name, name))
                description.append("<tr><th>%s (stddev)</th><td>%%(%s_stddev)s" % (name, name))
        sqlcols = ', '.join(sqlcols)
        description = "<h2>%(count)s</h2><table>" + ''.join(description) + "</table>"

        self.cur.execute("""
          select
             min(a.max_score::integer) as min,
             max(a.max_score::integer) as max
           from  
             appomatic_mapcluster_cluster a
           where
             a.score = a.max_score
             and a.score >= %(size)s
        """, {"size": size})
        scoremin, scoremax = self.cur.next()

        self.cur.execute("""
          select
             """ + sqlcols + """
           from  
             appomatic_mapcluster_cluster a
             join appomatic_mapcluster_cluster b on
               ST_DWithin(a.glocation, b.glocation, 7500)
             join """ + query + """ as c on
               b.reportnum = c.id
           where
             a.score = a.max_score
             and a.score >= %(size)s
           group by
             a.id,
             a.max_score
           order by
             a.max_score desc
        """, {"size": size})


        folder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}',
                                    'timeperiod-%s-%s' % (timeperiod[0].strftime("%s"), timeperiod[1].strftime("%s")),
                                    '%s:%s' % (timeperiod[0].strftime("%Y-%m-%d"), timeperiod[1].strftime("%Y-%m-%d")),
                                    '')
        doc.append(folder)

        seq = 0
        for row in dictreader(self.cur):
            style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s-%s" % (timeperiod, seq))
            icon_style = fastkml.styles.IconStyle(
                '{http://www.opengis.net/kml/2.2}',
                "style-%s-%s-icon" % (timeperiod, seq),
                scale=0.5 + 2 * (float(row['count'] - scoremin) / (scoremax - scoremin)),
                icon_href="http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png",
                color=color)
            style.append_style(icon_style)
            doc.append_style(style)
            placemark = fastkml.kml.Placemark('{http://www.opengis.net/kml/2.2}', "%s-%s" % (timeperiod, seq), "", description % row)
            placemark.geometry = shapely.wkt.loads(str(row['shape']))
            placemark.styleUrl = "#style-%s-%s" % (timeperiod, seq)
            folder.append(placemark)
            seq += 1



    def extract_reports(self, query, doc):
        folder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}', 'All reports', 'Reports', '')
        doc.append(folder)

        icons = [
            "http://maps.google.com/mapfiles/kml/shapes/open-diamond.png",
            "http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png",
            "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png",
            "http://maps.google.com/mapfiles/kml/shapes/placemark_square_highlight.png",
            "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png",
            "http://maps.google.com/mapfiles/kml/shapes/polygon.png",
            "http://maps.google.com/mapfiles/kml/shapes/star.png",
            "http://maps.google.com/mapfiles/kml/shapes/target.png",
            "http://maps.google.com/mapfiles/kml/shapes/triangle.png"]


        self.cur.execute("""
          select
            distinct grouping
          from
            """ + query + """ as a
        """)
        groupings = [row[0] for row in self.cur]

        for ind, typename in enumerate(groupings):
            style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s" % (typename,))
            icon_style = fastkml.styles.IconStyle(
                '{http://www.opengis.net/kml/2.2}',
                "style-%s-icon" % (typename,),
                scale=0.5,
                icon_href=icons[ind % len(icons)])
            style.append_style(icon_style)
            doc.append_style(style)

        for grouping in groupings:
            subfolder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}', grouping, grouping)
            folder.append(subfolder)

            #### Extract all selected reports from Mysql for import into GE
            self.cur.execute("""
              select
                *,
                ST_AsText(location) as shape
              from
                """ + query + """ as a 
              where
                grouping = %(grouping)s;
            """, {"grouping": grouping})

            for row in dictreader(self.cur):
                keys = row.keys()
                keys.sort()
                description = '<table>%s</table>' % (
                    '\n'.join('<tr><th>%s</th><td>%s</td></tr>' % (key, row[key])
                              for key in keys))
                placemark = fastkml.kml.Placemark('{http://www.opengis.net/kml/2.2}', "%(id)s" % row, "", description)
                placemark.geometry = shapely.wkt.loads(str(row['shape']))
                placemark.styleUrl = "#style-%s" % (grouping,)
                subfolder.append(placemark)


    def extract_kml(self, query, size, periods):
        kml = fastkml.kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
        kml.append(doc)

        self.cur.execute("truncate table appomatic_mapcluster_cluster")

        for timeperiod in periods:
            self.extract_clusters(query, size, timeperiod, doc)

        self.extract_reports(query, doc)

        return kml.to_string(prettyprint=True)


    def handle2(self, query, filename, size = 4, periods = [], *args, **options):
        periods = [(datetime.datetime.strptime(start, '%Y-%m-%d'),
                    datetime.datetime.strptime(end, '%Y-%m-%d'))
                   for start, end in (period.split(":")
                                      for period in periods)]
        if not periods:
            now = datetime.datetime.now()
            periods = [(now - datetime.timedelta(timeperiod), now)
                       for timeperiod in (12*30, 6*30, 3*30, 30)]
    
        try:
            with contextlib.closing(django.db.connection.cursor()) as cur:
                self.cur = cur

                with open(filename, "w") as f:
                    f.write(self.extract_kml(query, size, periods).encode('utf-8'))
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()

    def handle(self, *args, **options):
        try:
            return self.handle2(*args, **options)
        except Exception, e:
            print type(e), e
            import traceback
            traceback.print_exc()
            raise
