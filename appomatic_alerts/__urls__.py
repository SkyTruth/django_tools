from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^alerts/?$', 'appomatic_alerts.views.index'),
    (r'^alerts/subscribe/?$', 'appomatic_alerts.views.subscribe'),
    (r'^alerts/about/?$', 'appomatic_alerts.views.about'),
    (r'^alerts/api/?$', 'appomatic_alerts.views.api'),
    (r'^alerts/support/?$', 'appomatic_alerts.views.support'),
)
