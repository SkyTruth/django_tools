import django.contrib.admin
import appomatic_feedserver.models


django.contrib.admin.site.register(appomatic_feedserver.models.Feedtag)
django.contrib.admin.site.register(appomatic_feedserver.models.Feedsource)
django.contrib.admin.site.register(appomatic_feedserver.models.Feedentry)
class RssEmailSubscriptionAdmin(django.contrib.admin.ModelAdmin):
    list_display = ('active', 'email', 'name', 'interval_hours', 'last_update_sent', 'rss_url')
    list_filter = ('active','interval_hours')
    date_hierarchy = 'last_update_sent'
    search_fields = ('email', 'name', 'rss_url')
django.contrib.admin.site.register(appomatic_feedserver.models.RssEmailSubscription, RssEmailSubscriptionAdmin)
