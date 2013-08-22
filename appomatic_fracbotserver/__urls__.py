from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^fracbot/check-records/?$', 'appomatic_fracbotserver.views.check_records'),
)
