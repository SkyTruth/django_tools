import django.core.management.base
import optparse
import django.db
import fcdjangoutils.sqlutils
import contextlib
import numpy
import datetime
import sklearn.cluster


class Command(django.core.management.base.BaseCommand):
    help = """Clean up data from VIIRS
Usages:
viirs_cleanup
    """

    def handle(self, *args, **kwargs):
        try:
            return self.handle2(*args, **kwargs)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()

    def handle2(self, *args, **kwargs):
        with contextlib.closing(django.db.connection.cursor()) as readcur:
            with contextlib.closing(django.db.connection.cursor()) as writecur:
                readcur.execute("""
                    select
                      d1.id,
                      d1.filename
                    from
                      appomatic_mapimport_downloaded d1
                      left outer join appomatic_mapimport_downloaded d2 on
                        d1.id = d2.parent_id
                        and d2.src='VIIRS_CORRECTED_CLUSTERED'
                    where
                      d1.src = 'VIIRS_CORRECTED'
                      and d2.id is null
                    """)
                to_update = [row for row in readcur]

                for file_id, filename in to_update:
                    print "Cleaning up %s..." % filename
                    try:
                        readcur.execute("""
                            select count(*) from appomatic_mapdata_viirs where
                              src = 'VIIRS_CORRECTED'
                              and srcfile = %(srcfile)s

                              and "Temperature" > 1773
                              and "Temperature" != 1810
                              and "Temperature" < 5273.15

                        """, {'srcfile': filename})
                        nr_records = readcur.next()[0]
                        
                        readcur.execute("""
                            select * from appomatic_mapdata_viirs where
                              src = 'VIIRS_CORRECTED'
                              and srcfile = %(srcfile)s

                              and "Temperature" > 1773
                              and "Temperature" != 1810
                              and "Temperature" < 5273.15
                        """, {'srcfile': filename})
                        print "    Clustering %s records..." % nr_records

                        X = numpy.zeros((nr_records, 9))
                        for idx, row in enumerate(fcdjangoutils.sqlutils.dictreader(readcur)):
                                X[idx][0] = row['longitude'] and float(row['longitude']) or 0.0
                                X[idx][1] = row['latitude'] and float(row['latitude']) or 0.0
                                X[idx][2] = row['datetime'] and float(row['datetime'].strftime("%s")) or 0.0
                                X[idx][3] = row['RadiantOutput'] and float(row['RadiantOutput']) or 0.0
                                X[idx][4] = row['Temperature'] and float(row['Temperature']) or 0.0
                                X[idx][5] = row['RadiativeHeat'] and float(row['RadiativeHeat']) or 0.0
                                X[idx][6] = row['footprint'] and float(row['footprint']) or 0.0
                                X[idx][7] = row['SatZenithAngle'] and float(row['SatZenithAngle']) or 0.0
                                X[idx][8] = row['quality'] and float(row['quality']) or 0.0
                        
                        db = sklearn.cluster.DBSCAN(eps=0.013498916666666666, min_samples=3).fit(X[:,0:2])

                        for k in set(db.labels_):
                            points = X[(db.labels_ == k).nonzero()]

                            writecur.execute("""
                                insert into appomatic_mapdata_viirs (
                                  "src",
                                  "srcfile",
                                  "datetime",
                                  "name",
                                  "latitude",
                                  "longitude",
                                  "location",
                                  "RadiantOutput",
                                  "Temperature",
                                  "RadiativeHeat",
                                  "footprint",
                                  "SatZenithAngle",
                                  "SourceID",
                                  "quality")
                                values (
                                  'VIIRS_CORRECTED_CLUSTERED',
                                  %(filename)s,
                                  %(datetime)s,
                                  '',
                                  %(latitude)s,
                                  %(longitude)s,
                                  ST_SetSrid(ST_MakePoint(%(longitude)s, %(latitude)s), 4326),
                                  %(RadiantOutput)s,
                                  %(Temperature)s,
                                  %(RadiativeHeat)s,
                                  %(footprint)s,
                                  %(SatZenithAngle)s,
                                  '',
                                  %(quality)s)""",
                                {
                                    'filename': filename,
                                    'longitude': numpy.average(points[:,0]),
                                    'latitude': numpy.average(points[:,1]),
                                    'datetime': datetime.datetime.fromtimestamp(numpy.average(points[:,2])),
                                    'RadiantOutput': numpy.average(points[:,3]),
                                    'Temperature': numpy.average(points[:,4]),
                                    'RadiativeHeat': numpy.sum(points[:,5]),
                                    'footprint': numpy.sum(points[:,6]),
                                    'SatZenithAngle': numpy.average(points[:,7]),
                                    'quality': numpy.average(points[:,8])
                                    })

                        readcur.execute("""
                            insert into appomatic_mapimport_downloaded (src, filename, parent_id) values ('VIIRS_CORRECTED_CLUSTERED', %(filename)s, %(parent_id)s)
                        """, {'filename': filename, 'parent_id': file_id})

                    except Exception, e:
                        print "    Error loading file " + str(e)
                        import traceback
                        traceback.print_exc()
                        writecur.execute("rollback")
                        readcur.execute("rollback")
                    else:
                        writecur.execute("commit")
                        readcur.execute("commit")
