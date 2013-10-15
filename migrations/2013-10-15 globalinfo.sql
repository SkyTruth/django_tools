update appomatic_siteinfo_basemodel a set info = b.info from appomatic_siteinfo_well b where a.id = b.locationdata_ptr_id;
alter table appomatic_siteinfo_well drop column info;
update appomatic_siteinfo_basemodel a set info = b.info from appomatic_siteinfo_statusevent b where a.id = b.siteevent_ptr_id;
alter table appomatic_siteinfo_statusevent drop column info;
