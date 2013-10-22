import django.contrib.admin
import appomatic_mapcluster.models

django.contrib.admin.site.register(appomatic_mapcluster.models.Report)
django.contrib.admin.site.register(appomatic_mapcluster.models.Cluster)
django.contrib.admin.site.register(appomatic_mapcluster.models.Query)
