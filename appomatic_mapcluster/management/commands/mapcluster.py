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
import csv
import os.path

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))


class Command(django.core.management.base.BaseCommand):
    help = 'Calculates and exports clusters of events'
    args = '<query> <filename>'

    option_list = django.core.management.base.BaseCommand.option_list + (
        optparse.make_option('--template',
            action='store',
            dest='template',
            default=None,
            help='Tempplate file for descriptions'),
        optparse.make_option('--format',
            action='store',
            dest='format',
            default='kml',
            help='Export format. Supported formats: kml, csv.'),
        optparse.make_option('--size',
            action='store',
            type='int',
            dest='size',
            default=4,
            help='Minimum cluster size (number of events) for a cluster to be included in the output.'),
        optparse.make_option('--radius',
            action='store',
            type='int',
            dest='radius',
            default=7500,
            help='Cluster radius in meters within which events are included in the cluster.'),
        optparse.make_option('--period',
            action='append',
            dest='periods',
            default=[],
            help='Time period to cluster over, start and end dates separated by a colon, e.g. 2013-01-01:2013-02-01. This option can be given multiple times to give multiple date ranges.'),
        )

    def template_cluster_name(self, columns):
        return ""

    def template_cluster_description(self, columns):
        columnnames = columns.keys()
        columnnames.sort()
        description = []
        for name in columnnames:
            t = columns[name]
            if name == 'id': continue
            if t == 'NUMBER':
                description.append('<tr><th>%s (min)</th><td>%%(%s_min)s' % (name, name))
                description.append('<tr><th>%s (max)</th><td>%%(%s_max)s' % (name, name))
                description.append('<tr><th>%s (avg)</th><td>%%(%s_avg)s' % (name, name))
                description.append('<tr><th>%s (stddev)</th><td>%%(%s_stddev)s' % (name, name))
            elif t == 'DATETIME':
                description.append('<tr><th>%s (min)</th><td>%%(%s_min)s' % (name, name))
                description.append('<tr><th>%s (max)</th><td>%%(%s_max)s' % (name, name))
                description.append('<tr><th>%s (avg)</th><td>%%(%s_avg)s' % (name, name))
                description.append('<tr><th>%s (stddev)</th><td>%%(%s_stddev)s' % (name, name))
        return '<h2>%(count)s</h2><table>' + ''.join(description) + '</table>'

    def template_report_name(self, columns):
        return ""

    def template_report_description(self, columns):
        columnnames = columns.keys()
        columnnames.sort()
        description = []
        for name in columnnames:
            if name == 'id': continue
            description.append('<tr><th>%s</th><td>%%(%s)s' % (name, name))
        return '<h2>%(id)s</h2><table>' + ''.join(description) + '</table>'

    def sql_cluster_columns(self, columns):
        sqlcols = []
        for name, t in columns.iteritems():
            if name == 'id': continue
            if t == 'NUMBER':
                sqlcols.append('min(c."%s") as "%s_min"' % (name, name))
                sqlcols.append('max(c."%s") as "%s_max"' % (name, name))
                sqlcols.append('avg(c."%s") as "%s_avg"' % (name, name))
                sqlcols.append('stddev(c."%s") as "%s_stddev"' % (name, name))
            elif t == 'DATETIME':
                sqlcols.append('min(c."%s") as "%s_min"' % (name, name))
                sqlcols.append('max(c."%s") as "%s_max"' % (name, name))
                sqlcols.append('to_timestamp(avg(extract(\'epoch\' from c."%s"))) as "%s_avg"' % (name, name))
                sqlcols.append('stddev(extract(\'epoch\' from c."%s")) * interval \'1second\' as "%s_stddev"' % (name, name))
        return sqlcols


    def extract_columns(self, query):
        self.cur.execute("""
          select
            *
          from
            """ + query + """ as a
          limit 1
        """)

        return dict((name, ts[0])
                    for (name, ts) in ((column.name, 
                                        [name
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
                                         if column.type_code == t])
                                       for column in self.cur.description)
                    if ts)

    def extract_clusters(self, query, size, radius, timeperiod):
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

        columns = self.extract_columns(query)

        # Remove old data if any
        self.cur.execute("truncate table appomatic_mapcluster_cluster")

        #### Select the timeframe to work with
        filter = "true"
        args = {}
        if timeperiod is not None:
            filter = """
              datetime >= %(period_min)s and datetime <= %(period_max)s 
            """
            args["period_min"] = timeperiod[0]
            args["period_max"] = timeperiod[1]
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
        # self.cur.execute("update appomatic_mapcluster_cluster set buffer = st_buffer(location, %(radius)s)", {"radius": radius})

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
                        ST_DWithin(a.glocation, b.glocation, %(radius)s))
                     || '.' || reportnum)::double precision
        """, {"radius": radius})

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
                            ST_DWithin(a.glocation, b.glocation, %(radius)s))
        """, {"radius": radius})


        sqlcols = ["a.id",
                   "a.max_score::integer as count",
                   "ST_Y(ST_Centroid(ST_Collect(b.location))) as lat",
                   "ST_X(ST_Centroid(ST_Collect(b.location))) as lng",
                   "ST_AsText(ST_Centroid(ST_Collect(b.location))) as shape"]
        sqlcols.extend(self.sql_cluster_columns(columns))
        sqlcols = ', '.join(sqlcols)

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
               ST_DWithin(a.glocation, b.glocation, %(radius)s)
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
        """, {"size": size, "radius": radius})

        seq = 0
        for row in dictreader(self.cur):
            yield {
                "seq": seq,
                "color": color,
                "columns": columns,
                "scoremin": scoremin,
                "scoremax": scoremax,
                "description": self.template_cluster_description(columns),
                "name": self.template_cluster_name(columns),
                "row": row
                }
            seq += 1

    def extract_reports(self, query, periods):
        columns = self.extract_columns(query)

        description = self.template_report_description(columns)
        name = self.template_report_name(columns)

        #### Select the timeframe to work with
        filter = "true"
        args = {}
        if periods:
            q = []
            for ind, timeperiod in enumerate(periods):
                q.append("datetime >= %%(period%s_min)s and datetime <= %%(period%s_max)s" % (ind, ind))
                args["period%s_min" % (ind,)] = timeperiod[0]
                args["period%s_max" % (ind,)] = timeperiod[1]
            filter = '(%s)' % ' or '.join(q)

        self.cur.execute("""
          select
            distinct grouping
          from
            """ + query + """ as a
          where
        """ + filter, args)
        groupings = [[row[0]] for row in self.cur]

        for grouping in groupings:
            def getRows():
                groupargs = {"grouping": grouping[0]}
                groupargs.update(args)
                self.cur.execute("""
                  select
                    *,
                    ST_AsText(location) as shape
                  from
                    """ + query + """ as a 
                  where
                    grouping = %(grouping)s and
                """ + filter, groupargs)

                for row in dictreader(self.cur):
                    yield {'row': row, 'description': description, 'name': name}
            grouping.append(getRows())
        return groupings


    def extract_reports_kml(self, query, periods, doc):
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

        groupings = self.extract_reports(query, periods)

        for ind, (typename, rows) in enumerate(groupings):
            style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s" % (typename,))
            icon_style = fastkml.styles.IconStyle(
                '{http://www.opengis.net/kml/2.2}',
                "style-%s-icon" % (typename,),
                scale=0.5,
                icon_href=icons[ind % len(icons)])
            style.append_style(icon_style)
            doc.append_style(style)

        for (typename, rows) in groupings:
            subfolder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}', typename, typename)
            folder.append(subfolder)

            for info in rows:
                placemark = fastkml.kml.Placemark('{http://www.opengis.net/kml/2.2}', "%(id)s" % info['row'], info['name'] % info['row'], info['description'] % info['row'])
                placemark.geometry = shapely.wkt.loads(str(info['row']['shape']))
                placemark.styleUrl = "#style-%s" % (typename,)
                subfolder.append(placemark)



    def extract_clusters_kml(self, query, size, radius, timeperiod, doc):
        folder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}',
                                    'timeperiod-%s-%s' % (timeperiod[0].strftime("%s"), timeperiod[1].strftime("%s")),
                                    '%s:%s' % (timeperiod[0].strftime("%Y-%m-%d"), timeperiod[1].strftime("%Y-%m-%d")),
                                    '')
        doc.append(folder)

        for info in self.extract_clusters(query, size, radius, timeperiod):
            style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s-%s" % (timeperiod, info['seq']))
            if info['scoremax'] - info['scoremin']:
                scale = 0.5 + 2 * (float(info['row']['count'] - info['scoremin']) / (info['scoremax'] - info['scoremin']))
            else:
                scale = 1.0
            icon_style = fastkml.styles.IconStyle(
                '{http://www.opengis.net/kml/2.2}',
                "style-%s-%s-icon" % (timeperiod, info['seq']),
                scale=scale,
                icon_href="http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png",
                color=info['color'])
            style.append_style(icon_style)
            doc.append_style(style)
            placemark = fastkml.kml.Placemark('{http://www.opengis.net/kml/2.2}', "%s-%s" % (timeperiod, info['seq']), info['name'] % info['row'], info['description'] % info['row'])
            placemark.geometry = shapely.wkt.loads(str(info['row']['shape']))
            placemark.styleUrl = "#style-%s-%s" % (timeperiod, info['seq'])
            folder.append(placemark)


    def extract_kml(self, query, size, radius, periods):
        kml = fastkml.kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
        kml.append(doc)

        for timeperiod in periods:
            self.extract_clusters_kml(query, size, radius, timeperiod, doc)

        self.extract_reports_kml(query, periods, doc)

        return kml.to_string(prettyprint=True)


    def extract_clusters_csv(self, query, radius, size, timeperiod, doc):
        for info in self.extract_clusters(query, radius, size, timeperiod):
            point = shapely.wkt.loads(str(info['row']['shape']))
            info['row']['longitude'] = point.x
            info['row']['latitude'] = point.y
            info['row']['periodstart'] = timeperiod[0]
            info['row']['periodend'] = timeperiod[1]
            del info['row']['shape']

            if self.columns is None:
                self.columns = info['row'].keys()
                self.columns.sort()
                doc.writerow(self.columns)

            doc.writerow([info['row'][col] for col in self.columns])

    def extract_csv(self, query, size, radius, periods, doc):
        self.columns = None
        for timeperiod in periods:
            self.extract_clusters_csv(query, size, radius, timeperiod, doc)

    def handle2(self, query, filename, template=None, format='kml', size = 4, radius=7500, periods = [], *args, **options):
        if template:
            with open(os.path.expanduser(template)) as f:
                l = {}
                exec f in l
                for key, value in l.iteritems():
                    setattr(type(self), key, value) # hackety hack...

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
                    if format == 'kml':
                        f.write(self.extract_kml(query, size, radius, periods).encode('utf-8'))
                    elif format == 'csv':
                        self.extract_csv(query, size, radius, periods, csv.writer(f))
                    else:
                        raise Exception("Unsupported format")
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
