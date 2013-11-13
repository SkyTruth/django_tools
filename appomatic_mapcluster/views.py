import django.template
import django.shortcuts
import django.http
import appomatic_mapcluster.models
import appomatic_mapcluster.genclusters
import urllib

def index(request):
    queries = appomatic_mapcluster.models.Query.objects.all()
    return django.shortcuts.render(request, 'appomatic_mapcluster/index.html', {"queries": queries},
        content_type="text/html")


def cluster(request, name):
    query = appomatic_mapcluster.models.Query.objects.get(slug=name)
    
    contentTypes = {'kml': 'application/kml', 'csv': 'text/csv', 'csv_reports': 'text/csv'}
    ext = {'kml': 'kml', 'csv': 'csv', 'csv_reports': 'csv'}

    format = request.GET.get('format', 'kml')
    periods = None
    start = request.GET.get('startdate', '')
    end = request.GET.get('enddate', '')
    if start or end:
        periods = ["%s:%s" % (start, end)]

    response = django.http.HttpResponse(
        appomatic_mapcluster.genclusters.extract(
            query.name, query.query, query.template, format, query.size, query.radius, query_id=query.id, periods = periods),
        content_type=contentTypes[format])

    filename = query.name
    if periods:
        filename += ' ' + ', '.join(periods)
    filename += "." + ext[format]
    
    response['Content-Disposition'] = 'attachment; filename="%s"' % (filename,)

    return response
