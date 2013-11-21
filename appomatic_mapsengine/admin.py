import django.contrib.admin
import appomatic_appadmin.views
import appomatic_mapsengine.models
import appomatic_mapsengine.exporter
import django.http
import django.shortcuts
import json

class ExportAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('name', 'lastid', 'tableid', 'projectid', 'clear', 'access_list', 'tags', 'description')
    list_display_links = list_display
    search_fields = ('slug', 'name', 'description')

    actions = ["run_export"]

    def run_export(self, request, queryset):
        def exporter(out):
            appomatic_mapsengine.exporter.Exporter(queryset, out)
        return django.shortcuts.redirect(
            django.core.urlresolvers.reverse(
                "appomatic_appadmin.views.progress_display",
                kwargs={"pid": appomatic_appadmin.views.progressable(exporter)}) + "?description=Run%20export")

    run_export.short_description = "Run the export(s)"

django.contrib.admin.site.register(appomatic_mapsengine.models.Export, ExportAdmin)
