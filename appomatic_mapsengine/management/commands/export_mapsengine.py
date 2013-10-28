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
        appomatic_mapsengine.exporter.Exporter(
            appomatic_mapsengine.models.Export.objects.all())
