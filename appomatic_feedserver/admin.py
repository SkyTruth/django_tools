import django.contrib.admin
import appomatic_feedserver.models

django.contrib.admin.site.register(appomatic_feedserver.models.Feedtag)
django.contrib.admin.site.register(appomatic_feedserver.models.Feedsource)
django.contrib.admin.site.register(appomatic_feedserver.models.Feedentry)
