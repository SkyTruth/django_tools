import django.core.management.base
import appomatic_mapexport.kmlconvert
import appomatic_mapexport.djangorecords
import optparse
import contextlib


class Command(django.core.management.base.BaseCommand):
    args = "<filename>"
    help = 'Exports ais track as kml'
    option_list = django.core.management.base.BaseCommand.option_list + (
        optparse.make_option('--datetime__gte',
            help='Time minimum as epoch. Example: 1360127063'),
        optparse.make_option('--datetime__lte',
            help='Time maximum as epoch. Example: 1360127063'),
        optparse.make_option('--bbox',
            help='Bounding box. Example: -146.33282,-32.331075,-90.08282,-17.064477'),
        optparse.make_option('--timemin',
            help='Time minimum. Example: 2012-01-20 14:30:47 GMT+2'),
        optparse.make_option('--timemax',
            help='Time maximum. Example: 2012-01-20 14:30:47 GMT+2'),
        optparse.make_option('--latmin',
            help='Latitude minimum. Example: 53.11'),
        optparse.make_option('--latmax',
            help='Latitude maximum. Example: 53.11'),
        optparse.make_option('--lonmin',
            help='Longitude minimum. Example: 53.11'),
        optparse.make_option('--lonmax',
            help='Longitude maximum. Example: 53.11'),
        optparse.make_option('--mmsi',
            help='MMSI. Example: 319063000'),
        )

    def handle(self, filename, *args, **options):
        with contextlib.closing(open(filename, 'w')) as f:
            f.write(appomatic_mapexport.kmlconvert.convert(appomatic_mapexport.djangorecords.get_records(**options), filename))
