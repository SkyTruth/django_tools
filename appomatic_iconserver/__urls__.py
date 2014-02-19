from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^icon/?$', 'appomatic_iconserver.views.icon'),
)
