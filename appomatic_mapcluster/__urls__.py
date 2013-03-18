from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^cluster/?$', 'appomatic_mapcluster.views.index'),
    (r'^cluster/(?P<name>.*)/?$', 'appomatic_mapcluster.views.cluster'),
)
