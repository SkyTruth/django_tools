import django.contrib.admin
import appomatic_siteinfo.models

django.contrib.admin.site.register(appomatic_siteinfo.models.Operator)
class WellInline(django.contrib.admin.TabularInline):
    model = appomatic_siteinfo.models.Well
class SiteAdmin(django.contrib.admin.ModelAdmin):
    inlines = [WellInline]
    list_display = ('name', 'latitude', 'longitude')
    list_display_links = ('name', 'latitude', 'longitude')
    search_fields = ('name',)
django.contrib.admin.site.register(appomatic_siteinfo.models.Site, SiteAdmin)
class WellAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('api', 'site', 'latitude', 'longitude')
    list_display_links = ('api', 'site', 'latitude', 'longitude')
    list_filter = ('site',)
    search_fields = ('name', 'site__name')
django.contrib.admin.site.register(appomatic_siteinfo.models.Well, WellAdmin)
django.contrib.admin.site.register(appomatic_siteinfo.models.PermitEvent)
django.contrib.admin.site.register(appomatic_siteinfo.models.SpudEvent)
django.contrib.admin.site.register(appomatic_siteinfo.models.CommentEvent)
