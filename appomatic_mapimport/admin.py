import django.contrib.admin
import appomatic_mapimport.models

class DownloadedAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('src', 'filename', 'datetime')
    list_display_links = ('src', 'filename', 'datetime')
    list_filter = ('src',)
    date_hierarchy = 'datetime'
    search_fields = ('src', 'filename', 'datetime')
django.contrib.admin.site.register(appomatic_mapimport.models.Downloaded, DownloadedAdmin)
