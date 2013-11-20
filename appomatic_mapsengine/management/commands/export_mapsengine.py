import appomatic_mapsengine.exporter
import django.core.management.base

class Command(django.core.management.base.BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            return self.handle2(*args, **kwargs)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()

    def handle2(self, *args, **kwargs):
        q = appomatic_mapsengine.models.Export.objects.all()
        if args:
            filters = [django.db.models.Q(slug=arg) for arg in args]
            filter = filters[0]
            for nextfilter in filters[1:]:
                filter = filter | nextfilter
            q = q.filter(filter)
        appomatic_mapsengine.exporter.Exporter(q)
