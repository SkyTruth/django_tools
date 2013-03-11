import django.db
import django.core.management.base
import appomatic_mapexport.kmlconvert
import appomatic_mapexport.djangorecords
import optparse
import contextlib

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
                        ais.mmsi,
                        ais.datetime) as a
                   group by a.src, a.mmsi
                   having count(a.location) > 1) as b,
                   (select 2^generate_series(-20,20) as tolerance
                    union select null as tolerance) as c;
            """)
            cur.execute("commit")
