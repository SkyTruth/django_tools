import appomatic_siteinfo.models
import urllib
import django.http

def operator(request, id):
    return django.http.HttpResponse(
        appomatic_siteinfo.models.Operator.objects.get(id=id).render(request))

def site(request, id):
    return django.http.HttpResponse(
        appomatic_siteinfo.models.Site.objects.get(id=id).render(request))

def well(request, id):
    return django.http.HttpResponse(
        appomatic_siteinfo.models.Well.objects.get(id=id).render(request))

def event(request, id):
    return django.http.HttpResponse(
        appomatic_siteinfo.models.Event.objects.get(id=id).render(request))

