from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^mapexport/kml/?$', 'appomatic_mapexport.views.kmlformat'),
    (r'^mapexport/csv/?$', 'appomatic_mapexport.views.csvformat'),
)
