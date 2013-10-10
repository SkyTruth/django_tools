import django.db
import django.core.management.base
import appomatic_mapexport.kmlconvert
import appomatic_mapexport.djangorecords
import optparse
import contextlib
import shapely.wkb
import shapely.wkt
import fastkml.kml
import fastkml.styles
import datetime

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))

class Command(django.core.management.base.BaseCommand):
    help = 'Sets up views and stored procedures for map data'

    def extract_clusters(self, timeperiod, doc):
        if timeperiod is None:
            color = "ff00ffff"
        else:
            mincolor = (255, 00, 255, 00)
            maxcolor = (255, 00, 00, 255)
            div = (timeperiod-30) / (11*30.0) # Min time: 1 month, max time, 1 year
            color = "%02x%02x%02x%02x" % tuple(c[1]*div + c[0]*(1.0-div)
                                               for c in zip(mincolor, maxcolor))

        # Requires appomatic_nrccluster_nrcreport to have been set up with data

        # Remove old data if any
        self.cur.execute("truncate table appomatic_nrccluster_cluster")

        #### Select the area and timeframe to work with, set SRID (to Albers Conic Equal Area - Florida NAD83) and store in cluster table
        filter = ""
        args = {}
        if timeperiod is not None:
            filter = """
              and %(timeperiod)s >= extract(
                day
                from
                  (select
                     max(incident_datetime)
                   from
                     appomatic_nrccluster_nrcreport)
                  - incident_datetime)
            """
            args["timeperiod"] = timeperiod
        self.cur.execute("""
          insert into appomatic_nrccluster_cluster (
            reportnum, incident_datetime, incidenttype, location) 
          select
            reportnum,
            incident_datetime,
            incidenttype,
            st_transform(st_setsrid(st_makepoint(lng,lat), 4326), 3086)
          from
            appomatic_nrccluster_nrcreport
          where
            lat >=-90
            and lat <= 90
            and lng >= -180
            and lng <= 180
            """ + filter, args)

        # Create buffer
        self.cur.execute("update appomatic_nrccluster_cluster set buffer = st_buffer(location, 7500)")

        ### Compute score - all reports in buffer 
        ### Tack on the reportnum after the decimal place on the score
        ### so no two clusters will ever have the exact same score.
        ### This ensures that we don't get two overlapping clusters
        ### (with the same score, which would lead both of them to be
        ### included in the output)
        self.cur.execute("""
          update
            appomatic_nrccluster_cluster a
          set
            score = ((select                        count(*) as c
                      from
                        appomatic_nrccluster_cluster b
                      where
                        st_contains(a.buffer, b.location))
                     || '.' || reportnum)::double precision
        """)

        ### Set max_score equal to the highest score in the buffer 
        self.cur.execute("""
          update
            appomatic_nrccluster_cluster a
          set
             max_score = (select
                            max(score) as c
                          from
                            appomatic_nrccluster_cluster b
                          where
                            st_contains(a.buffer, b.location))
        """)

        #### get cluster centroids
        self.cur.execute("""
          select
            max_score::integer as count, 
            ST_Y((select
                    ST_Transform(ST_Centroid(ST_Collect(location)), 4326) as centroid
                  from
                    appomatic_nrccluster_cluster b
                  where
                    st_contains(a.buffer, b.location))) as lat,
            ST_X((select
                    ST_Transform(ST_Centroid(ST_Collect(location)), 4326) as centroid
                  from
                    appomatic_nrccluster_cluster b
                  where
                    st_contains(a.buffer, b.location))) as lng,
            ST_AsText((select
                    ST_Transform(ST_Centroid(ST_Collect(location)), 4326) as centroid
                  from
                    appomatic_nrccluster_cluster b
                  where
                    st_contains(a.buffer, b.location))) as shape
          from  
            appomatic_nrccluster_cluster a
          where
            score = max_score
            and score >= 4
          order by
            max_score desc
        """)

        if timeperiod is None:
            title = 'All time'
            description = 'Clusters of reports from any time'
        else:
            title = '%s days' % (timeperiod,)
            description = 'Clusters of reports from the last %s days' % (timeperiod,)

        folder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}', 'timeperiod-%s' % (timeperiod,), title, description)
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



    def extract_reports(self, doc):
        folder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}', 'All reports', 'Reports', '')
        doc.append(folder)

        icons = [
            "http://maps.google.com/mapfiles/kml/shapes/open-diamond.png",
#            "http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png",
            "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png",
#            "http://maps.google.com/mapfiles/kml/shapes/placemark_square_highlight.png",
            "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png",
            "http://maps.google.com/mapfiles/kml/shapes/polygon.png",
            "http://maps.google.com/mapfiles/kml/shapes/star.png",
            "http://maps.google.com/mapfiles/kml/shapes/target.png",
            "http://maps.google.com/mapfiles/kml/shapes/triangle.png"]


        self.cur.execute("""
          select
            distinct incidenttype
          from
            "NrcReleaseIncidents" 
          where
            region='gulf'
            and extract(day from NOW()-incident_datetime) <= 366
            and geocode_source = 'Explicit';
        """)
        incidenttypes = [row[0] for row in self.cur]

        for ind, typename in enumerate(incidenttypes):
            style = fastkml.styles.Style('{http://www.opengis.net/kml/2.2}', "style-%s" % (typename,))
            icon_style = fastkml.styles.IconStyle(
                '{http://www.opengis.net/kml/2.2}',
                "style-%s-icon" % (typename,),
                scale=0.5,
                icon_href=icons[ind % len(icons)])
            style.append_style(icon_style)
            doc.append_style(style)

        for incidenttype in incidenttypes:
            subfolder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}', incidenttype, incidenttype)
            folder.append(subfolder)

            #### Extract all selected reports from Mysql for import into GE
            self.cur.execute("""
              select
                reportnum,
                incident_datetime,
                incidenttype,
                description,
                cause,
                suspected_responsible_company,
                medium_affected,
                material_name,
                full_report_url,
                sheen_length,
                sheen_width,
                reported_spill_volume,
                min_spill_volume,
                release_type,
                lng,
                lat,
                ST_AsText(ST_Point(lng, lat)) as shape
              from
                "NrcReleaseIncidents" 
              where
                region='gulf'
                and extract(day from NOW()-incident_datetime) <= 366
                and geocode_source = 'Explicit'
                and incidenttype = %(incidenttype)s;
            """, {"incidenttype": incidenttype})

            for row in dictreader(self.cur):
                placemark = fastkml.kml.Placemark('{http://www.opengis.net/kml/2.2}', "%(reportnum)s" % row,
                  "",
                  """
                  <h2><a href="%(full_report_url)s">Report %(reportnum)s (%(reported_spill_volume)s) @ %(incident_datetime)s</a></h2>
                  <table>
                    <tr><th>Reportnum</th><td>%(reportnum)s</td></tr>
                    <tr><th>Time and date</th><td>%(incident_datetime)s</td></tr>
                    <tr><th>Incident type</th><td>%(incidenttype)s</td></tr>
                    <tr><th>Description</th><td>%(description)s</td></tr>
                    <tr><th>Cause</th><td>%(cause)s</td></tr>
                    <tr><th>Suspected responsible_company</th><td>%(suspected_responsible_company)s</td></tr>
                    <tr><th>Medium affected</th><td>%(medium_affected)s</td></tr>
                    <tr><th>Material name</th><td>%(material_name)s</td></tr>
                    <tr><th>Full report url</th><td>%(full_report_url)s</td></tr>
                    <tr><th>Sheen size (LxW)</th><td>%(sheen_length)s x %(sheen_width)s</td></tr>
                    <tr><th>Reported volume</th><td>%(reported_spill_volume)s</td></tr>
                    <tr><th>Minimum volume</th><td>%(min_spill_volume)s</td></tr>
                    <tr><th>Release type</th><td>%(release_type)s</td></tr>
                    <tr><th>Coordinates</th><td>%(lat)sN %(lng)sE</td></tr>
                  </table>
                  """ % row)
                placemark.geometry = shapely.wkt.loads(str(row['shape']))
                placemark.styleUrl = "#style-%s" % (incidenttype,)
                subfolder.append(placemark)


    def extract_kml(self):
        kml = fastkml.kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        doc = fastkml.kml.Document(
            ns,
            'nrd-cluster-%s' % (datetime.datetime.now().strftime('%Y-%m-%d'),),
            'NRC Clusters %s' % (datetime.datetime.now().strftime('%Y-%m-%d'),),
            'Cluster analysis of all recent NRC reports in the gulf of mexico that indicate a release of materials into the environment.')
        kml.append(doc)

        self.cur.execute("truncate table appomatic_nrccluster_nrcreport")
        self.cur.execute("truncate table appomatic_nrccluster_cluster")

        self.cur.execute("""
          insert into appomatic_nrccluster_nrcreport(
            geocode_source, reportnum, incident_datetime, incidenttype, lat, lng, location)
          select
            geocode_source, reportnum, incident_datetime, incidenttype, lat, lng, ST_MakePoint(lng, lat)
          from
            "NrcReleaseIncidents"
          where
            region='gulf'
            and extract(day from NOW()-incident_datetime) <= 366
            and geocode_source = 'Explicit';
        """)

        for timeperiod in (None, 12*30, 6*30, 3*30):
            self.extract_clusters(timeperiod, doc)

        self.extract_reports(doc)

        return kml.to_string(prettyprint=True)


    def handle(self, filename, *args, **options):
        try:
            with contextlib.closing(django.db.connection.cursor()) as cur:
                self.cur = cur

                with open(filename, "w") as f:
                    f.write(self.extract_kml().encode('utf-8'))
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()
