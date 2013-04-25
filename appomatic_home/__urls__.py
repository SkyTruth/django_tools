from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^/?$', 'appomatic_home.views.index'),
)
