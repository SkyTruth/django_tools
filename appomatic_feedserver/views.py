import django.template
import django.shortcuts
import django.http
import appomatic_feedserver.models
import shapely
import shapely.wkt
import fastkml.kml
import datetime
import uuid
import geojson
import fcdjangoutils.jsonview
import appomatic_mapdata.models
import csv
import StringIO

import django.db.backends.postgresql_psycopg2.base
import django.db.models.fields
import django.db.models.sql.query

django.db.backends.postgresql_psycopg2.base.DatabaseWrapper.operators['array_contains'] = '@> %s'
django.db.backends.postgresql_psycopg2.base.DatabaseWrapper.operators['array_contained_by'] = '<@ %s'
django.db.backends.postgresql_psycopg2.base.DatabaseWrapper.operators['array_overlaps'] = '&& %s'
django.contrib.gis.db.models.sql.query.GeoQuery.query_terms.add('array_contains')
django.contrib.gis.db.models.sql.query.GeoQuery.query_terms.add('array_contained_by')
django.contrib.gis.db.models.sql.query.GeoQuery.query_terms.add('array_overlaps')

def wrap_method(cls):
    def wrap(fn):
        old_fn = getattr(cls, fn.func_name)
        def wrapper(*arg, **kw):
            return fn(old_fn, *arg, **kw)
        setattr(cls, fn.func_name, wrapper)
    return wrap

@wrap_method(django.db.models.fields.Field)
def get_prep_lookup(old_fn, self, lookup_type, value):
    if lookup_type in ('array_contains', 'array_contained_by', 'array_overlaps'):
        return value
    return old_fn(self, lookup_type, value)

@wrap_method(django.db.models.fields.Field)
def get_db_prep_lookup(old_fn, self, lookup_type, value, connection,
                       prepared=False):
    if lookup_type in ('array_contains', 'array_contained_by', 'array_overlaps'):
        return ['{%s}' % ','.join(self.get_db_prep_value(value, connection=connection,
                                                        prepared=prepared))]
    return old_fn(self, lookup_type, value, connection, prepared)

class DictWrapper(object):
    def __init__(self, obj):
        self.obj = obj
    def __getitem__(self, name):
        return getattr(self.obj, name)

def tags(request):
    return django.http.HttpResponse(','.join(tag.name for tag in appomatic_feedserver.models.Feedtag.objects.all()),
                                    content_type='text/plain')

def feed(request, format):
    filter = {}
    limit = 50

    if 'l' in request.GET or 'BBOX' in request.GET:
        if 'l' in request.GET:
            lat1, lng1, lat2, lng2 = [float(x) for x in request.GET['l'].split(',')]
        elif 'BBOX' in request.GET:
            lng1, lat1, lng2, lat2 = [float(x) for x in request.GET['BBOX'].split(',')]
        filter['the_geom__contained'] = shapely.geometry.box(min(lng1, lng2), min(lat1, lat2), max(lng1, lng2), max(lat1, lat2))
    if 'dates' in request.GET:
        if ',' in request.GET['dates']:
            start, end = request.GET['dates'].split(',')
            start = datetime.datetime.strptime(start, '%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%Y-%m-%d')
            filter['incident_datetime__gte'] = start
            filter['incident_datetime__lte'] = end
        else:
            start = datetime.datetime.strptime(request.GET['dates'], '%Y-%m-%d')
            filter['incident_datetime__gte'] = start
    if 'd' in request.GET:
        filter['incident_datetime__gte'] = datetime.datetime.now() - datetime.timedelta(int(request.GET['d']))

    if 'tag' in request.GET:
        filter['tags__array_contains'] = request.GET['tag'].split(',')

    if 'n' in request.GET:
        limit = int(request.GET['n'])

    entries = appomatic_feedserver.models.Feedentry.objects.filter(**filter).order_by('published')[:limit]
    
    if format == 'kml':
        kml = fastkml.kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        doc = fastkml.kml.Document(ns, 'docid', 'doc name', 'doc description')
        kml.append(doc)

        for entry in entries:
            placemark = fastkml.kml.Placemark(ns, "entry-%s" % entry.id, entry.title, entry.content)
            placemark.geometry = shapely.wkt.loads(entry.the_geom.wkt) # Bah, GeoDjango does not support the geo interface :(
            doc.append(placemark)
        
        result = kml.to_string(prettyprint=True).encode('utf-8')
    elif format == 'geojson':
        features = []
        for entry in entries:
            geometry = fcdjangoutils.jsonview.from_json(
                geojson.dumps(
                    shapely.wkt.loads(
                        entry.the_geom.wkt)))
            feature = {"type": "Feature",
                       "geometry": geometry,
                       "properties": {'id': entry.id,
                                      'title': entry.title,
                                      'link': entry.link,
                                      'summary': entry.summary,
                                      'content': entry.content,
                                      'source': entry.source.name,
                                      'kml_url': entry.kml_url,
                                      'incident_datetime': entry.incident_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                                      'published': entry.published.strftime('%Y-%m-%d %H:%M:%S'),
                                      'regions': [{'src': region.src,
                                                   'name': region.name,
                                                   'code': region.code}
                                                  for region in appomatic_mapdata.models.Region.objects.filter(id__in = entry.regions)],
                                      'tags': entry.tags,
                                      'source_item_id': entry.source_item_id
                                      }}
            features.append(feature)
        result = fcdjangoutils.jsonview.to_json(
            {"type": "FeatureCollection",
             "features": features})
    elif format == 'csv':
        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(['id',
                         'lat',
                         'lng',
                         'title',
                         'link',
                         'summary',
                         'content',
                         'source',
                         'kml_url',
                         'incident_datetime',
                         'published',
                         'regions',
                         'tags',
                         'source_item_id'])
        for entry in entries:
            writer.writerow([entry.id,
                             entry.lat,
                             entry.lng,
                             entry.title,
                             entry.link,
                             entry.summary,
                             entry.content,
                             entry.source.name,
                             entry.kml_url,
                             entry.incident_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                             entry.published.strftime('%Y-%m-%d %H:%M:%S'),
                             ','.join(region.code
                                      for region in appomatic_mapdata.models.Region.objects.filter(id__in = entry.regions)),
                             ','.join(entry.tags),
                             entry.source_item_id
                             ])    
        result = f.getvalue()
    elif format == 'atom':
        result = django.template.loader.get_template(
            'appomatic_feedserver/feed.atom'
            ).render(
            django.template.RequestContext(
                    request,
                    {"entries": entries,
                     "now": datetime.datetime.now(),
                     "id": uuid.uuid4().urn}))
    else: # elif format == 'txt':
        format = 'txt'
        result = '\n'.join("%(title)s @ %(lat)sN %(lng)sE, %(incident_datetime)s (%(tags)s)" % DictWrapper(entry) for entry in entries)
        

    contentTypes = {'kml': 'application/kml', 'atom': 'application/atom+xml', 'geojson': 'application/json', 'csv': 'text/csv', 'txt': 'text/plain'}

    response = django.http.HttpResponse(result, content_type=contentTypes[format])

    response['Content-Disposition'] = 'attachment; filename="feed.%s"' % (format,)

    return response
