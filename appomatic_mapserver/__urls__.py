from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^map/?$', 'appomatic_mapserver.views.index'),
    (r'^mapserver/?$', 'appomatic_mapserver.views.mapserver'),
)
