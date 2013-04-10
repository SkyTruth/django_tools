alter table appomatic_mapdata_vessel add column "src" varchar(128) NOT NULL default '';
alter table appomatic_mapdata_vessel add column "srcfile" varchar(1024);

alter table region add column "srcfile" varchar(1024);
alter table appomatic_mapdata_ais add column "srcfile" varchar(1024);
alter table appomatic_mapdata_aispath add column "srcfile" varchar(1024);
alter table appomatic_mapdata_sar add column "srcfile" varchar(1024);
alter table appomatic_mapdata_viirs add column "srcfile" varchar(1024);
