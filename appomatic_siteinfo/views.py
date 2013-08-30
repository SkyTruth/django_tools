import appomatic_siteinfo.models
import urllib
import django.http
import csv
import datetime

def basemodel(request, guuid=None, model="BaseModel"):
    style = None
    # Handle endless pagination
    if 'querystring_key' in request.REQUEST:
        style = request.REQUEST['querystring_key'] + ".html"
    if guuid is None:
        return getattr(appomatic_siteinfo.models, model).list_render(request, style=style, as_response = True)
    else:
        return appomatic_siteinfo.models.BaseModel.objects.get(guuid=guuid).render(request, style=style, as_response = True)

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

def clustersitelist(request):
    results = {'results': appomatic_siteinfo.models.Site.objects.filter(
            latitude__gte = request.GET['latmin'],
            longitude__gte = request.GET['lonmin'],
            datetime__gte = datetime.datetime.utcfromtimestamp(float(request.GET['timemin'])),
            latitude__lte = request.GET['latmax'],
            longitude__lte = request.GET['lonmax'],
            datetime__lte = datetime.datetime.utcfromtimestamp(float(request.GET['timemax'])))}
    results.update(request.GET.items())
    return django.shortcuts.render(request, 'appomatic_siteinfo/clustersitelist.html', results)
