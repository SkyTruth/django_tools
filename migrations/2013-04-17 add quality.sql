alter table appomatic_mapdata_ais add column "quality" double precision NOT NULL default 1.0;
alter table appomatic_mapdata_sar add column "quality" double precision NOT NULL default 1.0;
alter table appomatic_mapdata_viirs add column "quality" double precision NOT NULL default 1.0;
