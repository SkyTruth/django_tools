import django.db
import django.core.management.base
import appomatic_siteinfo.models
import sys
import contextlib

class Command(django.core.management.base.BaseCommand):
    help = 'Sets up views and stored procedures for map data'
 
    def handle(self, *args, **options):
        with contextlib.closing(django.db.connection.cursor()) as cur:
            cur.execute("select count(*) from (select guuid from appomatic_siteinfo_basemodel group by guuid having count(*) > 1) as a")
            total = float(cur.next()[0])
            cur.execute("select guuid from appomatic_siteinfo_basemodel group by guuid having count(*) > 1")
            for (idx, (guuid,)) in enumerate(cur):
                sys.stdout.write("%f.4:" % (idx / total))
                objs = appomatic_siteinfo.models.BaseModel.objects.filter(guuid=guuid)
                masterobj = objs[0]
                for obj in objs[1:]:
                    obj.merge(masterobj)
                    sys.stdout.write(".")
                sys.stdout.write("\n")

                
