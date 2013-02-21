import django.db
import django.core.management.base
import appomatic_mapexport.kmlconvert
import appomatic_mapexport.djangorecords
import optparse
import contextlib

class Command(django.core.management.base.BaseCommand):
    help = 'Sets up views and stored procedures for map data'
 
    def handle(self, *args, **options):
        with contextlib.closing(django.db.connection.cursor()) as cur:
            cur.execute("begin")
            cur.execute("delete from appomatic_mapdata_aispath")
            cur.execute("""
              insert into
                appomatic_mapdata_aispath (src, mmsi, timemin, timemax, tolerance, line)
              select
                src, mmsi, timemin, timemax, tolerance, line
              from
                appomatic_mapdata_ais_path_view
            """)
            cur.execute("commit")
