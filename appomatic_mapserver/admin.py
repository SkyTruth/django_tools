import django.contrib.admin
import appomatic_mapserver.models

django.contrib.admin.site.register(appomatic_mapserver.models.Application)
class LayerAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('application', 'name', 'backend_type', 'type', 'template')
    list_filter = ('application', 'backend_type', 'type', 'template')
    search_fields = ("name", "application__name")
django.contrib.admin.site.register(appomatic_mapserver.models.Layer, LayerAdmin)
