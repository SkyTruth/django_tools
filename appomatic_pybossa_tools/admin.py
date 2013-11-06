import django.contrib.admin
import appomatic_appadmin.views
import appomatic_pybossa_tools.models
import appomatic_pybossa_tools.importer
import django.http
import django.shortcuts
import json

class ServerAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('name', 'url')
    list_display_links = list_display
    search_fields = list_display
django.contrib.admin.site.register(appomatic_pybossa_tools.models.Server, ServerAdmin)
class AppAdmin(django.contrib.admin.ModelAdmin):
    actions = ["run_import"]
    def run_import(self, request, queryset):
        def importer(out):
            appomatic_pybossa_tools.importer.Importer(queryset, out)
        return django.shortcuts.redirect(
            django.core.urlresolvers.reverse(
                "appomatic_appadmin.views.progress_display",
                kwargs={"pid": appomatic_appadmin.views.progressable(importer)}) + "?description=Run%20import")
    run_import.short_description = "Run the imports(s)"
    list_display = ('server', 'name')
    list_display_links = list_display
    list_filter = ('server',)
    search_fields = list_display
django.contrib.admin.site.register(appomatic_pybossa_tools.models.App, AppAdmin)
class TaskAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('app', 'taskid')
    list_display_links = list_display
    list_filter = ('app',)
    search_fields = list_display
django.contrib.admin.site.register(appomatic_pybossa_tools.models.Task, TaskAdmin)
class AnswerAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('task', 'answerid')
    list_display_links = list_display
    list_filter = ('task',)
    search_fields = list_display
django.contrib.admin.site.register(appomatic_pybossa_tools.models.Answer, AnswerAdmin)
class GeoAnswerAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('answer', 'latitude', 'longitude')
    list_display_links = list_display
    list_filter = ('answer',)
    search_fields = list_display
django.contrib.admin.site.register(appomatic_pybossa_tools.models.GeoAnswer, GeoAnswerAdmin)
