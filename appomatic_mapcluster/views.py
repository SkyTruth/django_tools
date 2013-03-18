import django.template
import django.shortcuts
import django.http
import appomatic_mapcluster.models
import appomatic_mapcluster.genclusters

def index(request):
    queries = appomatic_mapcluster.models.Query.objects.all()
    return django.shortcuts.render(request, 'appomatic_mapcluster/index.html', {"queries": queries},
        content_type="text/html")


def cluster(request, name):
    query = appomatic_mapcluster.models.Query.objects.get(slug=name)
    
    contentTypes = {'kml': 'application/kml', 'csv': 'text/csv'}


    periods = None
    start = request.GET.get('startdate', '')
    end = request.GET.get('enddate', '')
    if start or end:
        periods = ["%s:%s" % (start, end)]

    response = django.http.HttpResponse(
        appomatic_mapcluster.genclusters.extract(
            query.query, query.template, query.format, query.size, query.radius, periods = periods),
        content_type=contentTypes[query.format])

    response['Content-Disposition'] = 'attachment; filename="%s.%s"' % (query.name, query.format,)

    return response
