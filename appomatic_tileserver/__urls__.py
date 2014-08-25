from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^log/?$', 'appomatic_tileserver.views.log'),
    url(r'^workspace/?$', 'appomatic_tileserver.views.workspace'),
    url(r'^tiles/(?P<bbox>[^/]*)$', 'appomatic_tileserver.views.index', {"tileset": "tileset"}),
    url(r'^tiles/(?P<tileset>[^/]*)/series/?$', 'appomatic_tileserver.views.series'),
    url(r'^tiles/(?P<tileset>[^/]*)/(?P<bbox>[^/]*)$', 'appomatic_tileserver.views.index'),
)
