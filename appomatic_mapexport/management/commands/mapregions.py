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

    def extract_kml(self):
        kml = fastkml.kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        doc = fastkml.kml.Document(ns, 'regions', 'Regions', 'Region names and codes used by SkyTruth')
        kml.append(doc)

        self.cur.execute("""
          select
            distinct src
          from
            region
        """)
        srcs = [row[0] for row in self.cur]

        for src in srcs:
            folder = fastkml.kml.Folder('{http://www.opengis.net/kml/2.2}', src, src)
            doc.append(folder)

            self.cur.execute("""
              select
                src,
                name,
                code,
                ST_AsText(the_geom) as the_geom
              from
                region
              where
                src = %(src)s
            """, {'src': src})

            for row in dictreader(self.cur):
                keys = row.keys()
                keys.sort()
                placemark = fastkml.kml.Placemark('{http://www.opengis.net/kml/2.2}', "%(code)s" % row, "%(name)s" % row, "%(name)s (%(code)s, from %(src)s)" % row)
                placemark.geometry = shapely.wkt.loads(str(row['the_geom']))
                folder.append(placemark)

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
