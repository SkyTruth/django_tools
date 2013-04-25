import django.db
import django.core.management.base
import appomatic_mapexport.kmlconvert
import appomatic_mapexport.djangorecords
import optparse
import contextlib
from django.conf import settings

class Command(django.core.management.base.BaseCommand):
    help = 'Sets up views and stored procedures for map data'
 
    def handle(self, *args, **options):
        with contextlib.closing(django.db.connection.cursor()) as cur:
            cur.execute("drop view if exists appomatic_mapdata_viirsfilteredview")
            cur.execute("""
              create view
                appomatic_mapdata_viirsfilteredview as
              select
                v.*, r.code as regioncode, r.id as regionid, r.name as regionname
              from
                appomatic_mapdata_viirs as v
                join region as r on
                  ST_Contains(r.the_geom, v.location)
              where
                "Temperature" > 2073 -- 2073K = 1800C, stuff below that is probably natural fires
            """)
            cur.execute("""
              create or replace function appomatic_mapdata_ais_insert()
                returns trigger as
              $BODY$
                declare
                  loc geometry;
                begin
                  loc := st_setsrid(st_makepointm(new.longitude, new.latitude, extract(epoch from new.datetime)), (4326));

                  if exists (select 1 from appomatic_mapdata_ais as ais where ais.mmsi = new.mmsi and ais.datetime = new.datetime) then
                    -- this record already exists.  Need to turn this into an update
                    -- and return null to cancel the insert
                    update
                      appomatic_mapdata_ais as ais
                    set
                      location = loc,
                      true_heading = new.true_heading,
                      sog = new.sog,
                      cog = new.cog,
                      latitude = new.latitude,
                      longitude = new.longitude
                    where
                      ais.mmsi = new.mmsi
                      and ais.datetime = new.datetime;
                    return null;
                  else
                    new.location := loc;
                    return new;
                  end if;
                end;
              $BODY$
                language plpgsql volatile
                cost 100;
            """)

            cur.execute("drop trigger if exists appomatic_mapdata_ais_insert on appomatic_mapdata_ais")
            cur.execute("""
              create trigger appomatic_mapdata_ais_insert
                before insert
                on appomatic_mapdata_ais
                for each row
                execute procedure appomatic_mapdata_ais_insert();
            """)

            cur.execute("drop view if exists appomatic_mapdata_ais_path_view")
            cur.execute("""
              create view appomatic_mapdata_ais_path_view as
               select
                 src,
                 mmsi,
                 tolerance,
                 case
                   when tolerance is null then line
                   else ST_Simplify(line, tolerance)
                 end as line,
                 timemin,
                 timemax
                from
                  (select
                     a.src,
                     a.mmsi,
                     st_makeline(a.location) as line,
                     min(a.datetime) as timemin,
                     max(a.datetime) as timemax
                   from
                     (select
                        ais.src,
                        ais.mmsi,
                        ais.datetime,
                        ais.latitude,
                        ais.longitude,
                        ais.true_heading,
                        ais.sog,
                        ais.cog,
                        ais.location
                      from
                        appomatic_mapdata_ais as ais
                      order by
                        ais.src,
                        ais.mmsi,
                        ais.datetime) as a
                   group by a.src, a.mmsi
                   having count(a.location) > 1
                   union select
                     'ALL' as src,
                     a.mmsi,
                     st_makeline(a.location) as line,
                     min(a.datetime) as timemin,
                     max(a.datetime) as timemax
                   from
                     (select
                        ais.src,
                        ais.mmsi,
                        ais.datetime,
                        ais.latitude,
                        ais.longitude,
                        ais.true_heading,
                        ais.sog,
                        ais.cog,
                        ais.location
                      from
                        appomatic_mapdata_ais as ais
                      order by
                        ais.src,
                        ais.mmsi,
                        ais.datetime) as a
                   group by a.mmsi
                   having count(a.location) > 1
                  ) as b,
                  (select 2^generate_series(%(TOLERANCE_BASE_MIN)s,%(TOLERANCE_BASE_MAX)s) as tolerance
                   union select null as tolerance) as c;
            """, {'TOLERANCE_BASE_MAX': settings.TOLERANCE_BASE_MAX,
                  'TOLERANCE_BASE_MIN': settings.TOLERANCE_BASE_MIN})

            cur.execute("""
              drop view if exists appomatic_mapdata_ais_calculated_speeds_view;
              create view appomatic_mapdata_ais_calculated_speeds_view as
              select
                ais.*,
                next.id next_id,
                next.src next_src,
                next.datetime next_datetime,
                next.latitude next_latitude,
                next.longitude next_longitude,
                next.true_heading next_true_heading,
                next.sog next_sog,
                next.cog next_cog,
                next.location next_location,
                next.srcfile next_srcfile,
                next.quality next_quality,
                st_distance(ais.location::geography, next.location::geography) / 1852.0 distance,
                next.datetime - ais.datetime timediff,
                (st_distance(ais.location::geography, next.location::geography) / 1852.0)
                 / ((extract(epoch from next.datetime) - extract(epoch from ais.datetime)) / 60 / 60) speed
              from
                appomatic_mapdata_ais ais
                join appomatic_mapdata_ais next on
                  ais.latitude <= 90 and ais.latitude >= -90 and ais.longitude <= 180 and ais.longitude >= -180
                  and next.latitude <= 90 and next.latitude >= -90 and next.longitude <= 180 and next.longitude >= -180
                  and next.mmsi = ais.mmsi
                  and next.datetime = (
                    select
                      min(between.datetime)
                    from
                      appomatic_mapdata_ais between
                    where
                      between.mmsi = ais.mmsi
                      and between.datetime > ais.datetime);
            """)
            
            cur.execute("""
              drop table if exists appomatic_mapdata_ais_calculated_speeds;
              create table appomatic_mapdata_ais_calculated_speeds as select * from appomatic_mapdata_ais_calculated_speeds_view limit 0;
            """)

            cur.execute("commit")
