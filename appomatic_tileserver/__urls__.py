from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^tiles/(?P<bbox>[^/]*)$', 'appomatic_tileserver.views.index', {"tileset": "tileset"}),
    url(r'^tiles/(?P<tileset>[^/]*)/(?P<bbox>[^/]*)$', 'appomatic_tileserver.views.index'),
)
