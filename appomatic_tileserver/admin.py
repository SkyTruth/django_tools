import django.contrib.admin
import appomatic_tileserver.models

django.contrib.admin.site.register(appomatic_tileserver.models.Workspace)
django.contrib.admin.site.register(appomatic_tileserver.models.Log)
