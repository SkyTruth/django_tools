import appomatic_fracbotserver.models
import django.contrib.admin

django.contrib.admin.site.register(appomatic_fracbotserver.models.State)
django.contrib.admin.site.register(appomatic_fracbotserver.models.County)
class ClientAdmin(django.contrib.admin.ModelAdmin):
    inlines = []
    list_display = ('id', 'ip', 'domain', 'agent')
    list_display_links = ('id', 'ip', 'domain', 'agent')
    search_fields = ('id', 'ip', 'domain', 'agent')
django.contrib.admin.site.register(appomatic_fracbotserver.models.Client, ClientAdmin)
django.contrib.admin.site.register(appomatic_fracbotserver.models.ActivityType)
class ActivityAdmin(django.contrib.admin.ModelAdmin):
    inlines = []
    list_display = ('client', 'type', 'amount', 'datetime')
    list_display_links = ('client', 'type', 'amount', 'datetime')
    search_fields = ('client','type')
django.contrib.admin.site.register(appomatic_fracbotserver.models.Activity, ActivityAdmin)
