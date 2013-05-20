import appomatic_siteinfo.models
import urllib
import django.http

def basemodel(request, id):
    return django.http.HttpResponse(
        appomatic_siteinfo.models.BaseModel.objects.get(id=id).render(request))
