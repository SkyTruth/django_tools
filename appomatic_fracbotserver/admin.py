import appomatic_fracbotserver.models
import django.contrib.admin

django.contrib.admin.site.register(appomatic_fracbotserver.models.State)
django.contrib.admin.site.register(appomatic_fracbotserver.models.County)
django.contrib.admin.site.register(appomatic_fracbotserver.models.Client)
django.contrib.admin.site.register(appomatic_fracbotserver.models.ActivityType)
class ActivityAdmin(django.contrib.admin.ModelAdmin):
    inlines = []
    list_display = ('client', 'type', 'datetime')
    list_display_links = ('client', 'type', 'datetime')
    search_fields = ('client','type')
django.contrib.admin.site.register(appomatic_fracbotserver.models.Activity, ActivityAdmin)
