create table ais_path as
 select
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
       a.mmsi,
       st_makeline(a.location) as line,
       min(a.datetime) as timemin,
       max(a.datetime) as timemax
     from
       (select
          ais.seqid,
          ais.datetime,
          ais.mmsi,
          ais.latitude,
          ais.longitude,
          ais.true_heading,
          ais.sog,
          ais.cog,
          ais.location
        from ais
        order by
          ais.mmsi,
          ais.datetime) as a
     group by a.mmsi
     having count(a.location) > 1) as b,
     (select 2^generate_series(-20,20) as tolerance
      union select null as tolerance) as c;


create index ais_path_line_idx on ais_path using gist (line);
create index ais_path_timemin_idx on ais_path (timemin);
create index ais_path_timemax_idx on ais_path (timemax);
create index ais_path_tolerance_idx on ais_path (tolerance);
