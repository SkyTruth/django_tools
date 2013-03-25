import django.contrib.admin
import appomatic_mapserver.models

django.contrib.admin.site.register(appomatic_mapserver.models.Application)
django.contrib.admin.site.register(appomatic_mapserver.models.Layer)
