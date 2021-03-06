import django.db
import django.core.management.base
import appomatic_mapdata.models
import appomatic_mapcluster.genclusters
import optparse
import contextlib
import shapely.wkb
import shapely.wkt
import fastkml.kml
import fastkml.styles
import psycopg2
import optparse
import datetime
import csv
import os.path

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))


class Command(django.core.management.base.BaseCommand):
    help = 'Calculates and exports clusters of events'
    args = '<query> <filename>'

    option_list = django.core.management.base.BaseCommand.option_list + (
        optparse.make_option('--list',
            action='store_true',
            dest='list',
            default=False,
            help='List pre-defined queries'),
        optparse.make_option('--name',
            action='store',
            dest='name',
            default='',
            help='Document name'),
        optparse.make_option('--template',
            action='store',
            dest='template',
            default=None,
            help='Tempplate file for descriptions'),
        optparse.make_option('--format',
            action='store',
            dest='format',
            default='kml',
            help='Export format. Supported formats: kml, csv.'),
        optparse.make_option('--size',
            action='store',
            type='int',
            dest='size',
            default=None,
            help='Minimum cluster size (number of events) for a cluster to be included in the output.'),
        optparse.make_option('--radius',
            action='store',
            type='int',
            dest='radius',
            default=None,
            help='Cluster radius in meters within which events are included in the cluster.'),
        optparse.make_option('--period',
            action='append',
            dest='periods',
            default=[],
            help='Time period to cluster over, start and end dates separated by a colon, e.g. 2013-01-01:2013-02-01. This option can be given multiple times to give multiple date ranges.'),
        )

    def handle2(self, query = None, filename = None, *args, **options):
        if options["list"]:
            for qobj in appomatic_mapcluster.models.Query.objects.all():
                print qobj.slug
            return
        try:
            qobj = appomatic_mapcluster.models.Query.objects.get(slug=query)
        except:
            if options["size"] is None: options["size"] = 4
            if options["radius"] is None: options["radius"] = 7500
        else:
            query = qobj.query
            options["query_id"] = qobj.id
            options["template"] = options["template"] or qobj.template
            if options["size"] is None: options["size"] = qobj.size
            if options["radius"] is None: options["radius"] = qobj.radius
        name = options.pop('name', None)
        if not name: name = os.path.splitext(os.path.split(filename)[1])[0]
        with open(filename, "w") as f:
            f.write(appomatic_mapcluster.genclusters.extract(name, query, *args, **options))

    def handle(self, *args, **options):
        try:
            return self.handle2(*args, **options)
        except Exception, e:
            print type(e), e
            import traceback
            traceback.print_exc()
            raise
