from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^tiles/(?P<bbox>.*)$', 'appomatic_tileserver.views.index'),
)
