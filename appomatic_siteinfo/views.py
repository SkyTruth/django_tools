import appomatic_siteinfo.models
import urllib
import django.http

def basemodel(request, id):
    return django.http.HttpResponse(
        appomatic_siteinfo.models.BaseModel.objects.get(id=id).render(request))

def search(request):
    query = request.GET['query']

    results = []
    results.append({'title': 'Matching companies',
                    'items': appomatic_siteinfo.models.Company.search(query)})
    results.append({'title': 'Matching chemicals',
                    'items': appomatic_siteinfo.models.Chemical.search(query)})
    results.append({'title': 'Matching sites',
                    'items': appomatic_siteinfo.models.Site.search(query)})
    results.append({'title': 'Matching wells',
                    'items': appomatic_siteinfo.models.Well.search(query)})

    for pos in xrange(len(results)-1, -1, -1):
        if not results[pos]['items']:
            del results[pos]

    if not len(results):
        results.append({'title': 'No results found'})

    return django.shortcuts.render(request, 'appomatic_siteinfo/search.html', {"results": results, "query": query})
