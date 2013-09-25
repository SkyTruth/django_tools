alter table appomatic_siteinfo_basemodel add column "info" text;
alter table appomatic_siteinfo_basemodel add column "typename" varchar(256);

update appomatic_siteinfo_basemodel a set info = b.info from appomatic_siteinfo_operatorinfoevent b where a.id = b.operatorevent_ptr_id;
update appomatic_siteinfo_basemodel a set info = b.info from appomatic_siteinfo_site b where a.id = b.locationdata_ptr_id;
update appomatic_siteinfo_basemodel a set info = b.info from appomatic_siteinfo_chemicalusageeventchemical b where a.id = b.basemodel_ptr_id;


update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.Chemical' from appomatic_siteinfo_chemical b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.ChemicalAlias' from appomatic_siteinfo_chemicalalias b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.ChemicalPurpose' from appomatic_siteinfo_chemicalpurpose b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.ChemicalPurposeAlias' from appomatic_siteinfo_chemicalpurposealias b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.ChemicalUsageEventChemical' from appomatic_siteinfo_chemicalusageeventchemical b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.CommentEvent' from appomatic_siteinfo_commentevent b where b.userevent_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.Company' from appomatic_siteinfo_company b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.CompanyAlias' from appomatic_siteinfo_companyalias b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.FracEvent' from appomatic_siteinfo_fracevent b where b.chemicalusageevent_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.InspectionEvent' from appomatic_siteinfo_inspectionevent b where b.operatorinfoevent_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.PermitEvent' from appomatic_siteinfo_permitevent b where b.operatorinfoevent_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.PollutionEvent' from appomatic_siteinfo_pollutionevent b where b.operatorinfoevent_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.Site' from appomatic_siteinfo_site b where b.locationdata_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.SiteAlias' from appomatic_siteinfo_sitealias b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.SpudEvent' from appomatic_siteinfo_spudevent b where b.operatorinfoevent_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.Status' from appomatic_siteinfo_status b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.StatusAlias' from appomatic_siteinfo_statusalias b where b.basemodel_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.StatusEvent' from appomatic_siteinfo_statusevent b where b.siteevent_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.ViolationEvent' from appomatic_siteinfo_violationevent b where b.operatorinfoevent_ptr_id = a.id;
update appomatic_siteinfo_basemodel a set typename = 'appomatic_siteinfo.models.Well' from appomatic_siteinfo_well b where b.locationdata_ptr_id = a.id;

alter table appomatic_siteinfo_operatorinfoevent drop column info;
alter table appomatic_siteinfo_site drop column info;
alter table appomatic_siteinfo_chemicalusageeventchemical drop column info;
