from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^tag/?$', 'appomatic_feedserver.views.tags'),
    (r'^rss/?$', 'appomatic_feedserver.views.feed', {'format': 'rss'}),
    (r'^kml/?$', 'appomatic_feedserver.views.feed', {'format': 'kml'}),
    (r'^txt/?$', 'appomatic_feedserver.views.feed', {'format': 'txt'}),
)
