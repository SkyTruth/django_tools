import django.template
import django.shortcuts
import django.http
import django.db
import contextlib
import datetime
import math
import appomatic_mapexport.kmlconvert
import appomatic_mapexport.csvconvert
import appomatic_mapexport.djangorecords

def kmlformat(request):
    return django.http.HttpResponse(
        appomatic_mapexport.kmlconvert.convert(appomatic_mapexport.djangorecords.get_records(**dict(request.GET.items())), 'extract2kml'),
        mimetype="text/plain",
        status=200)

def csvformat(request):
    return django.http.HttpResponse(
        appomatic_mapexport.csvconvert.convert(appomatic_mapexport.djangorecords.get_records(**dict(request.GET.items()))),
        mimetype="text/plain",
        status=200)
