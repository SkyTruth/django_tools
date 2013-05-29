import appomatic_siteinfo.models
import urllib
import django.http

def basemodel(request, id):
    return django.http.HttpResponse(
        appomatic_siteinfo.models.BaseModel.objects.get(id=id).render(request))

def search(request):
    query = request.GET['query']

    results = []
    results.append({'title': 'Company',
                    'items': appomatic_siteinfo.models.Company.search(query)})
    results.append({'title': 'Sites',
                    'items': appomatic_siteinfo.models.Site.search(query)})
    results.append({'title': 'Wells',
                    'items': appomatic_siteinfo.models.Well.search(query)})

    return django.shortcuts.render(request, 'appomatic_siteinfo/search.html', {"results": results, "query": query})
