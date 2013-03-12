import django.db
import django.core.management.base
import appomatic_mapdata.models
import optparse
import contextlib
import shapely.wkb
import shapely.wkt
import fastkml.kml
import fastkml.styles

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))

class Command(django.core.management.base.BaseCommand):
    help = 'Calculates and exports clusters of events'

    def extract_clusters(self, query, timeperiod, doc):
        if timeperiod is None:
            color = "ff00ffff"
        else:
            mincolor = (255, 00, 255, 00)
            maxcolor = (255, 00, 00, 255)
            div = (timeperiod-30) / (11*30.0) # Min time: 1 month, max time, 1 year
            color = "%02x%02x%02x%02x" % tuple(c[1]*div + c[0]*(1.0-div)
                                               for c in zip(mincolor, maxcolor))

        # Remove old data if any
        self.cur.execute("truncate table appomatic_mapcluster_cluster")

        #### Select the area and timeframe to work with, set SRID (to Albers Conic Equal Area - Florida NAD83) and store in cluster table
        filter = "true"
        args = {}
        if timeperiod is not None:
            filter = """
              %(timeperiod)s >= extract(
                day
                from
                  (select
                     max(datetime)
                   from
                     """ + query + """ as a)
                  - datetime)
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

        #### get cluster centroids
        self.cur.execute("""
          select
            max_score::integer as count, 
            ST_Y((select
                    ST_Centroid(ST_Collect(location)) as centroid
                  from
                    appomatic_mapcluster_cluster b
                  where
                    ST_DWithin(a.glocation, b.glocation, 7500))) as lat,
            ST_X((select
                    ST_Centroid(ST_Collect(location)) as centroid
                  from
                    appomatic_mapcluster_cluster b
                  where
                    ST_DWithin(a.glocation, b.glocation, 7500))) as lng,
            ST_AsText((select
                    ST_Centroid(ST_Collect(location)) as centroid
                  from
                    appomatic_mapcluster_cluster b
                  where
                    ST_DWithin(a.glocation, b.glocation, 7500))) as shape
          from  
            appomatic_mapcluster_cluster a
          where
            score = max_score
            and score >= 4
          order by
            max_score desc
        """)

        folder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}', 'timeperiod-%s' % (timeperiod,), '%s days' % (timeperiod,), '')
        doc.append(folder)

        seq = 0
        for row in dictreader(self.cur):
            style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s-%s" % (timeperiod, seq))
            icon_style = fastkml.styles.IconStyle(
                '{http://www.opengis.net/kml/2.2}',
                "style-%s-%s-icon" % (timeperiod, seq),
                scale=0.5 + 0.01 * row['count'],
                icon_href="http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png",
                color=color)
            style.append_style(icon_style)
            doc.append_style(style)
            placemark = fastkml.kml.Placemark('{http://www.opengis.net/kml/2.2}', "%s-%s" % (timeperiod, seq), "",  """<h2>%(count)s</h2>""" % row)
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


    def extract_kml(self, query):
        kml = fastkml.kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
        kml.append(doc)

        self.cur.execute("truncate table appomatic_mapcluster_cluster")

        for timeperiod in (None, 12*30, 6*30, 3*30):
            self.extract_clusters(query, timeperiod, doc)

        self.extract_reports(query, doc)

        return kml.to_string(prettyprint=True)


    def handle(self, query, filename, *args, **options):
        try:
            with contextlib.closing(django.db.connection.cursor()) as cur:
                self.cur = cur

                with open(filename, "w") as f:
                    f.write(self.extract_kml(query).encode('utf-8'))
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()
