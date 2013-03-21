from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^tag/?$', 'appomatic_feedserver.views.tags'),
    (r'^feed/(?P<format>.*)/?$', 'appomatic_feedserver.views.feed'),
)
