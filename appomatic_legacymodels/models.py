# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.contrib.gis.db import models

import datetime

class X23051Incidents(models.Model):
    reportnum = models.IntegerField(blank=True, null=True)
    calltype = models.CharField(max_length=16, blank=True)
    recieved_datetime = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    incident_datetime = models.DateTimeField(blank=True, null=True)
    incidenttype = models.CharField(max_length=32, blank=True)
    cause = models.CharField(max_length=32, blank=True)
    location = models.TextField(blank=True)
    state = models.CharField(max_length=255, blank=True)
    nearestcity = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=255, blank=True)
    suspected_responsible_company = models.CharField(max_length=255, blank=True)
    medium_affected = models.CharField(max_length=255, blank=True)
    material_name = models.CharField(max_length=255, blank=True)
    full_report_url = models.CharField(max_length=255, blank=True)
    materials_url = models.CharField(max_length=255, blank=True)
    sheen_length = models.FloatField(blank=True, null=True)
    sheen_width = models.FloatField(blank=True, null=True)
    reported_spill_volume = models.FloatField(blank=True, null=True)
    min_spill_volume = models.FloatField(blank=True, null=True)
    areaid = models.CharField(max_length=32, blank=True)
    blockid = models.CharField(max_length=32, blank=True)
    platform_letter = models.CharField(max_length=16, blank=True)
    zip = models.CharField(max_length=16, blank=True)
    affected_area = models.CharField(max_length=32, blank=True)
    geocode_source = models.CharField(max_length=16, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = '23051_Incidents'

class AleghenyForestPa(models.Model):
    gid = models.IntegerField(primary_key=True)
    fid = models.FloatField(db_column='FID', blank=True, null=True) # Field name made lowercase.
    the_geom = models.PolygonField(srid=26917, blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'Alegheny_Forest_PA'

class Areacodemap(models.Model):
    # id = models.IntegerField(primary_key=True)
    pattern = models.CharField(max_length=64)
    area_code = models.CharField(max_length=2)
    class Meta:
        managed = False
        db_table = 'AreaCodeMap'

class BoemreSizes(models.Model):
    # id = models.IntegerField(blank=True, null=True)
    min_gal = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True)
    max_gal = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True)
    label = models.CharField(max_length=20, blank=True)
    class Meta:
        managed = False
        db_table = 'Boemre_sizes'

class Bottask(models.Model):
    # id = models.IntegerField()
    bot = models.CharField(max_length=20)
    name = models.CharField(max_length=32)
    process_interval_secs = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'BotTask'

class Bottaskerror(models.Model):
    task_id = models.IntegerField()
    bot = models.CharField(max_length=32)
    code = models.CharField(max_length=16)
    message = models.CharField(max_length=1023, blank=True)
    time_stamp = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'BotTaskError'

class Bottaskparams(models.Model):
    task_id = models.IntegerField()
    bot = models.CharField(max_length=20)
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=1024, blank=True)
    class Meta:
        managed = False
        db_table = 'BotTaskParams'

class Bottaskstatus(models.Model):
    task_id = models.IntegerField()
    bot = models.CharField(max_length=32)
    status = models.CharField(max_length=16)
    time_stamp = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'BotTaskStatus'

class CoPermits(models.Model):
    seqid = models.CharField(max_length=23, primary_key=True)
    ft_id = models.IntegerField()
    county_name = models.CharField(max_length=20, blank=True)
    received_date = models.DateField(blank=True, null=True)
    posted_date = models.DateField(blank=True, null=True)
    operator_name = models.CharField(max_length=50, blank=True)
    operator_number = models.CharField(max_length=20, blank=True)
    approved_date = models.DateField(blank=True, null=True)
    api = models.CharField(max_length=20, blank=True)
    type_of_permit = models.CharField(max_length=8, blank=True)
    well_name = models.CharField(max_length=50, blank=True)
    well_number = models.CharField(max_length=20, blank=True)
    proposed_td = models.FloatField(blank=True, null=True)
    well_location = models.CharField(max_length=50, blank=True)
    footage_call = models.CharField(max_length=50, blank=True)
    field = models.CharField(max_length=50, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    elevation = models.CharField(max_length=20, blank=True)
    federal_state_lease = models.CharField(max_length=20, blank=True)
    record_url = models.CharField(max_length=255, blank=True)
    class Meta:
        managed = False
        db_table = 'CO_Permits'

class Cogisinspection(models.Model):
    st_id = models.IntegerField(primary_key=True)
    doc_num = models.CharField(max_length=15)
    county_code = models.CharField(max_length=10, blank=True)
    county_name = models.CharField(max_length=30, blank=True)
    date = models.DateField(blank=True, null=True)
    doc_href = models.CharField(max_length=120, blank=True)
    loc_id = models.CharField(max_length=15, blank=True)
    operator = models.CharField(max_length=60, blank=True)
    insp_api_num = models.CharField(max_length=30, blank=True)
    insp_status = models.CharField(max_length=15, blank=True)
    insp_overall = models.CharField(max_length=30, blank=True)
    ir_pass_fail = models.CharField(max_length=10, blank=True)
    fr_pass_fail = models.CharField(max_length=10, blank=True)
    violation = models.CharField(max_length=10, blank=True)
    site_lat = models.CharField(max_length=20, blank=True)
    site_lng = models.CharField(max_length=20, blank=True)
    time_stamp = models.DateTimeField()
    ft_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'CogisInspection'

class Cogisspill(models.Model):
    st_id = models.IntegerField(primary_key=True)
    doc_num = models.CharField(max_length=15)
    county_code = models.CharField(max_length=10, blank=True)
    county_name = models.CharField(max_length=30, blank=True)
    date = models.DateField(blank=True, null=True)
    doc_href = models.CharField(max_length=120, blank=True)
    facility_id = models.CharField(max_length=15, blank=True)
    operator_num = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=60, blank=True)
    groundwater = models.CharField(max_length=10, blank=True)
    surfacewater = models.CharField(max_length=10, blank=True)
    berm_contained = models.CharField(max_length=10, blank=True)
    spill_area = models.CharField(max_length=15, blank=True)
    spill_lat = models.CharField(max_length=20, blank=True)
    spill_lng = models.CharField(max_length=20, blank=True)
    ft_id = models.IntegerField(blank=True, null=True)
    time_stamp = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'CogisSpill'

class DefunctBlockcentroid(models.Model):
    area = models.FloatField(db_column='AREA') # Field name made lowercase.
    perimeter = models.FloatField(db_column='PERIMETER') # Field name made lowercase.
    prot_numbe = models.CharField(db_column='PROT_NUMBE', max_length=7) # Field name made lowercase.
    prot_aprv_field = models.CharField(db_column='PROT_APRV_', max_length=11) # Field name made lowercase. Field renamed because it ended with '_'.
    block_numb = models.CharField(db_column='BLOCK_NUMB', max_length=6) # Field name made lowercase.
    blk_fed_ap = models.CharField(db_column='BLK_FED_AP', max_length=11) # Field name made lowercase.
    area_code = models.CharField(db_column='AREA_CODE', max_length=2) # Field name made lowercase.
    ac_lab = models.CharField(db_column='AC_LAB', max_length=8) # Field name made lowercase.
    block_lab = models.CharField(db_column='BLOCK_LAB', max_length=6) # Field name made lowercase.
    mms_region = models.CharField(db_column='MMS_REGION', max_length=1) # Field name made lowercase.
    orig_fid = models.IntegerField(db_column='ORIG_FID') # Field name made lowercase.
    point_x = models.FloatField(db_column='POINT_X') # Field name made lowercase.
    point_y = models.FloatField(db_column='POINT_Y') # Field name made lowercase.
    blockid = models.CharField(max_length=6, blank=True)
    class Meta:
        managed = False
        db_table = 'DEFUNCT_BlockCentroid'

class DefunctBlockcentroidnew(models.Model):
    area = models.FloatField(db_column='AREA') # Field name made lowercase.
    perimeter = models.FloatField(db_column='PERIMETER') # Field name made lowercase.
    prot_numbe = models.CharField(db_column='PROT_NUMBE', max_length=7) # Field name made lowercase.
    prot_aprv_field = models.CharField(db_column='PROT_APRV_', max_length=11) # Field name made lowercase. Field renamed because it ended with '_'.
    block_numb = models.CharField(db_column='BLOCK_NUMB', max_length=6) # Field name made lowercase.
    blk_fed_ap = models.CharField(db_column='BLK_FED_AP', max_length=11) # Field name made lowercase.
    area_code = models.CharField(db_column='AREA_CODE', max_length=2) # Field name made lowercase.
    ac_lab = models.CharField(db_column='AC_LAB', max_length=8) # Field name made lowercase.
    block_lab = models.CharField(db_column='BLOCK_LAB', max_length=6) # Field name made lowercase.
    mms_region = models.CharField(db_column='MMS_REGION', max_length=1) # Field name made lowercase.
    orig_fid = models.IntegerField(db_column='ORIG_FID') # Field name made lowercase.
    y = models.FloatField()
    x = models.FloatField()
    class Meta:
        managed = False
        db_table = 'DEFUNCT_BlockCentroidNew'

class DefunctFeedentry(models.Model):
    # id = models.CharField(primary_key=True, max_length=36)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    updated = models.DateTimeField()
    summary = models.TextField(blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    content = models.TextField(blank=True)
    source_id = models.IntegerField()
    kml_url = models.CharField(max_length=255, blank=True)
    published = models.DateTimeField()
    published_seq = models.IntegerField()
    incident_datetime = models.DateTimeField()
    source_item_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'DEFUNCT_FeedEntry'

class DefunctFracfocus(models.Model):
    seqid = models.CharField(max_length=23)
    ft_id = models.IntegerField()
    api_nr = models.CharField(max_length=20, blank=True)
    job_date = models.DateField(blank=True, null=True)
    state = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=20, blank=True)
    operator_name = models.CharField(max_length=50, blank=True)
    well_name = models.CharField(max_length=50, blank=True)
    well_type = models.CharField(max_length=10, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    datum = models.CharField(max_length=8, blank=True)
    blob_key = models.CharField(max_length=180, blank=True)
    class Meta:
        managed = False
        db_table = 'DEFUNCT_FracFocus'

class FtNrcIncidentReports(models.Model):
    time_stamp = models.DateTimeField(blank=True, null=True)
    reportnum = models.IntegerField(blank=True, null=True)
    calltype = models.CharField(max_length=16, blank=True)
    recieved_datetime = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    incident_datetime = models.DateTimeField(blank=True, null=True)
    incidenttype = models.CharField(max_length=32, blank=True)
    cause = models.CharField(max_length=32, blank=True)
    location = models.CharField(max_length=255, blank=True)
    affected_area = models.CharField(max_length=32, blank=True)
    state = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=32, blank=True)
    nearestcity = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=16, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    areaid = models.CharField(max_length=32, blank=True)
    blockid = models.CharField(max_length=32, blank=True)
    platform_letter = models.CharField(max_length=16, blank=True)
    suspected_responsible_company = models.CharField(max_length=255, blank=True)
    medium_affected = models.CharField(max_length=255, blank=True)
    material_name = models.CharField(max_length=255, blank=True)
    full_report_url = models.CharField(max_length=255, blank=True)
    materials_url = models.CharField(max_length=255, blank=True)
    sheen_size_length = models.CharField(max_length=16, blank=True)
    sheen_size_width = models.CharField(max_length=16, blank=True)
    class Meta:
        managed = False
        db_table = 'FT_NRC_Incident_Reports'

class FtTest(models.Model):
    seq = models.IntegerField(primary_key=True)
    time_stamp = models.DateTimeField()
    name = models.CharField(max_length=30, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    ft_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'FT_Test'

class Feedentrytag(models.Model):
    feed_entry_id = models.CharField(max_length=36)
    tag = models.CharField(max_length=64)
    comment = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'FeedEntryTag'

class FracfocuschemicalOld(models.Model):
    seqid = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    report_seqid = models.IntegerField()
    api = models.CharField(max_length=20)
    fracture_date = models.DateField()
    row = models.IntegerField()
    trade_name = models.CharField(max_length=200, blank=True)
    supplier = models.CharField(max_length=50, blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    ingredients = models.CharField(max_length=100, blank=True)
    cas_number = models.CharField(max_length=50, blank=True)
    additive_concentration = models.FloatField(blank=True, null=True)
    hf_fluid_concentration = models.FloatField(blank=True, null=True)
    comments = models.CharField(max_length=200, blank=True)
    class Meta:
        managed = False
        db_table = 'FracFocusChemical_old'

class FracfocuschemicalOld2(models.Model):
    seqid = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    report_seqid = models.IntegerField()
    api = models.CharField(max_length=20)
    fracture_date = models.DateField()
    row = models.IntegerField()
    trade_name = models.CharField(max_length=200, blank=True)
    supplier = models.CharField(max_length=50, blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    ingredients = models.CharField(max_length=100, blank=True)
    cas_number = models.CharField(max_length=50, blank=True)
    additive_concentration = models.FloatField(blank=True, null=True)
    hf_fluid_concentration = models.FloatField(blank=True, null=True)
    comments = models.CharField(max_length=200, blank=True)
    class Meta:
        managed = False
        db_table = 'FracFocusChemical_old2'

class Fracfocuspdf(models.Model):
    seqid = models.IntegerField(primary_key=True)
    downloaded = models.DateTimeField()
    pdf = models.BinaryField(blank=True, null=True)
    filename = models.CharField(max_length=100, blank=True)
    class Meta:
        managed = False
        db_table = 'FracFocusPDF'

class Fracfocusparse(models.Model):
    seqid = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    api = models.CharField(max_length=20)
    fracture_date = models.DateField()
    state = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=20, blank=True)
    operator = models.CharField(max_length=50, blank=True)
    well_name = models.CharField(max_length=50, blank=True)
    production_type = models.CharField(max_length=10, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    datum = models.CharField(max_length=8, blank=True)
    true_vertical_depth = models.FloatField(blank=True, null=True)
    total_water_volume = models.FloatField(blank=True, null=True)
    extracted = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'FracFocusParse'

class Fracfocusparsechemical(models.Model):
    seqid = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    report_seqid = models.IntegerField()
    api = models.CharField(max_length=20)
    fracture_date = models.DateField()
    row = models.IntegerField()
    trade_name = models.CharField(max_length=200, blank=True)
    supplier = models.CharField(max_length=50, blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    ingredients = models.CharField(max_length=200, blank=True)
    cas_number = models.CharField(max_length=50, blank=True)
    additive_concentration = models.FloatField(blank=True, null=True)
    hf_fluid_concentration = models.FloatField(blank=True, null=True)
    ingredient_weight = models.FloatField(blank=True, null=True)
    comments = models.CharField(max_length=200, blank=True)
    class Meta:
        managed = False
        db_table = 'FracFocusParseChemical'

class Fracfocusreport(models.Model):
    seqid = models.AutoField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    pdf_seqid = models.IntegerField()
    api = models.CharField(max_length=20)
    fracture_date = models.DateField()
    state = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=20, blank=True)
    operator = models.CharField(max_length=50, blank=True)
    well_name = models.CharField(max_length=50, blank=True)
    production_type = models.CharField(max_length=10, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    datum = models.CharField(max_length=8, blank=True)
    true_vertical_depth = models.FloatField(blank=True, null=True)
    total_water_volume = models.FloatField(blank=True, null=True)
    published = models.DateTimeField(default = datetime.datetime.now)
    total_water_weight = models.FloatField(blank=True, null=True)
    total_pct_in_fluid = models.FloatField(blank=True, null=True)
    water_pct_in_fluid = models.FloatField(blank=True, null=True)
    total_hf_weight = models.FloatField(blank=True, null=True)
    err_code = models.CharField(max_length=20, blank=True)
    err_field = models.CharField(max_length=20, blank=True)
    err_comment = models.CharField(max_length=500, blank=True)
    class Meta:
        managed = False
        db_table = 'FracFocusReport'

class Fracfocusreportchemical(models.Model):
    seqid = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    pdf_seqid = models.IntegerField()
    api = models.CharField(max_length=20)
    fracture_date = models.DateField()
    row = models.IntegerField()
    trade_name = models.CharField(max_length=200, blank=True)
    supplier = models.CharField(max_length=50, blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    ingredients = models.CharField(max_length=200, blank=True)
    cas_number = models.CharField(max_length=50, blank=True)
    additive_concentration = models.FloatField(blank=True, null=True)
    hf_fluid_concentration = models.FloatField(blank=True, null=True)
    ingredient_weight = models.FloatField(blank=True, null=True)
    comments = models.CharField(max_length=200, blank=True)
    weight = models.FloatField(blank=True, null=True)
    cas_type = models.CharField(max_length=20, blank=True)
    class Meta:
        managed = False
        db_table = 'FracFocusReportChemical'

class FracfocusreportOld(models.Model):
    seqid = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    api = models.CharField(max_length=20)
    fracture_date = models.DateField()
    state = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=20, blank=True)
    operator = models.CharField(max_length=50, blank=True)
    well_name = models.CharField(max_length=50, blank=True)
    production_type = models.CharField(max_length=10, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    datum = models.CharField(max_length=8, blank=True)
    true_vertical_depth = models.FloatField(blank=True, null=True)
    total_water_volume = models.FloatField(blank=True, null=True)
    extracted = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'FracFocusReport_old'

class FracfocusreportOld2(models.Model):
    seqid = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    api = models.CharField(max_length=20)
    fracture_date = models.DateField()
    state = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=20, blank=True)
    operator = models.CharField(max_length=50, blank=True)
    well_name = models.CharField(max_length=50, blank=True)
    production_type = models.CharField(max_length=10, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    datum = models.CharField(max_length=8, blank=True)
    true_vertical_depth = models.FloatField(blank=True, null=True)
    total_water_volume = models.FloatField(blank=True, null=True)
    extracted = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'FracFocusReport_old2'

class Fracfocusscrape(models.Model):
    seqid = models.IntegerField(primary_key=True)
    scraped = models.DateTimeField()
    ft_id = models.IntegerField(blank=True, null=True)
    api = models.CharField(max_length=20, blank=True)
    job_date = models.DateField(blank=True, null=True)
    state = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=20, blank=True)
    operator = models.CharField(max_length=50, blank=True)
    well_name = models.CharField(max_length=50, blank=True)
    well_type = models.CharField(max_length=10, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    datum = models.CharField(max_length=8, blank=True)
    pdf_download_attempts = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'FracFocusScrape'

class GompolygonDrawn(models.Model):
    gid = models.IntegerField(primary_key=True)
    # id = models.IntegerField(db_column='ID', blank=True, null=True) # Field name made lowercase.
    the_geom = models.GeometryField(srid=4269, blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'GOMPolygon_drawn'

class Geocodecache(models.Model):
    field_key = models.CharField(db_column='_key', primary_key=True, max_length=50) # Field renamed because it started with '_'.
    updated = models.DateTimeField()
    lat = models.FloatField()
    lng = models.FloatField()
    class Meta:
        managed = False
        db_table = 'GeocodeCache'

class Huc10Monongahela(models.Model):
    gid2 = models.IntegerField(primary_key=True)
    gid = models.IntegerField(blank=True, null=True)
    huc_8 = models.CharField(max_length=255, blank=True)
    huc_10 = models.CharField(max_length=255, blank=True)
    acres = models.FloatField(blank=True, null=True)
    hu_10_name = models.CharField(max_length=255, blank=True)
    the_geom = models.PolygonField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'HUC10_Monongahela'

class LaLeaseBlocks(models.Model):
    # id = models.IntegerField(primary_key=True)
    wkt_geom = models.CharField(max_length=40)
    lat = models.FloatField()
    lng = models.FloatField()
    area_id = models.CharField(max_length=8)
    block_id = models.CharField(max_length=8)
    dxf_text = models.CharField(db_column='DXF_TEXT', max_length=8) # Field name made lowercase.
    area_name = models.CharField(db_column='AREA_NAME', max_length=32) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'LA_Lease_Blocks'

class Leaseblockcentroid(models.Model):
    # id = models.IntegerField(primary_key=True)
    areaid = models.CharField(max_length=8)
    blockid = models.CharField(max_length=8)
    lat = models.FloatField()
    lng = models.FloatField()
    state = models.CharField(max_length=8)
    class Meta:
        managed = False
        db_table = 'LeaseBlockCentroid'

class MonongahelaHuc6Watershed(models.Model):
    gid2 = models.IntegerField(primary_key=True)
    gid = models.IntegerField(blank=True, null=True)
    region = models.CharField(db_column='REGION', max_length=255, blank=True) # Field name made lowercase.
    subregion = models.CharField(db_column='SUBREGION', max_length=255, blank=True) # Field name made lowercase.
    basin = models.CharField(db_column='BASIN', max_length=255, blank=True) # Field name made lowercase.
    huc_2 = models.CharField(db_column='HUC_2', max_length=255, blank=True) # Field name made lowercase.
    huc_4 = models.CharField(db_column='HUC_4', max_length=255, blank=True) # Field name made lowercase.
    huc_6 = models.CharField(db_column='HUC_6', max_length=255, blank=True) # Field name made lowercase.
    the_geom = models.PolygonField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'Monongahela_HUC6_Watershed'

class MonongahelaHuc8Watersheds(models.Model):
    gid2 = models.IntegerField(primary_key=True)
    gid = models.IntegerField(blank=True, null=True)
    objectid = models.IntegerField(db_column='OBJECTID', blank=True, null=True) # Field name made lowercase.
    region = models.CharField(db_column='REGION', max_length=255, blank=True) # Field name made lowercase.
    subregion = models.CharField(db_column='SUBREGION', max_length=255, blank=True) # Field name made lowercase.
    basin = models.CharField(db_column='BASIN', max_length=255, blank=True) # Field name made lowercase.
    subbasin = models.CharField(db_column='SUBBASIN', max_length=255, blank=True) # Field name made lowercase.
    huc_2 = models.CharField(db_column='HUC_2', max_length=255, blank=True) # Field name made lowercase.
    huc_4 = models.CharField(db_column='HUC_4', max_length=255, blank=True) # Field name made lowercase.
    huc_6 = models.CharField(db_column='HUC_6', max_length=255, blank=True) # Field name made lowercase.
    huc_8 = models.CharField(db_column='HUC_8', max_length=255, blank=True) # Field name made lowercase.
    acres = models.FloatField(db_column='ACRES', blank=True, null=True) # Field name made lowercase.
    sq_miles = models.FloatField(db_column='SQ_MILES', blank=True, null=True) # Field name made lowercase.
    hu_8_state = models.CharField(db_column='HU_8_STATE', max_length=255, blank=True) # Field name made lowercase.
    fips_c = models.CharField(db_column='FIPS_C', max_length=255, blank=True) # Field name made lowercase.
    shape_leng = models.FloatField(db_column='SHAPE_Leng', blank=True, null=True) # Field name made lowercase.
    shape_area = models.FloatField(db_column='SHAPE_Area', blank=True, null=True) # Field name made lowercase.
    the_geom = models.PolygonField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'Monongahela_HUC8_watersheds'

class NightfireFile(models.Model):
    # id = models.IntegerField(primary_key=True)
    filename = models.CharField(unique=True, max_length=60)
    time_stamp = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'Nightfire_file'

class NightfireRecord(models.Model):
    file_num = models.BigIntegerField()
    # id = models.BigIntegerField(db_column='ID') # Field name made lowercase.
    lat_gmtco = models.FloatField(db_column='Lat_GMTCO', blank=True, null=True) # Field name made lowercase.
    lon_gmtco = models.FloatField(db_column='Lon_GMTCO', blank=True, null=True) # Field name made lowercase.
    cm_iicmo = models.BigIntegerField(db_column='CM_IICMO', blank=True, null=True) # Field name made lowercase.
    cot_ivcop = models.FloatField(db_column='COT_IVCOP', blank=True, null=True) # Field name made lowercase.
    eps_ivcop = models.FloatField(db_column='EPS_IVCOP', blank=True, null=True) # Field name made lowercase.
    qf1_ivcop = models.BigIntegerField(db_column='QF1_IVCOP', blank=True, null=True) # Field name made lowercase.
    qf2_ivcop = models.BigIntegerField(db_column='QF2_IVCOP', blank=True, null=True) # Field name made lowercase.
    qf3_ivcop = models.BigIntegerField(db_column='QF3_IVCOP', blank=True, null=True) # Field name made lowercase.
    total_rad = models.FloatField(db_column='Total_Rad', blank=True, null=True) # Field name made lowercase.
    bb_temp = models.BigIntegerField(db_column='BB_Temp', blank=True, null=True) # Field name made lowercase.
    m07_rad = models.FloatField(db_column='M07_Rad', blank=True, null=True) # Field name made lowercase.
    m08_rad = models.FloatField(db_column='M08_Rad', blank=True, null=True) # Field name made lowercase.
    m10_rad = models.FloatField(db_column='M10_Rad', blank=True, null=True) # Field name made lowercase.
    m12_rad = models.FloatField(db_column='M12_Rad', blank=True, null=True) # Field name made lowercase.
    m13_rad = models.FloatField(db_column='M13_Rad', blank=True, null=True) # Field name made lowercase.
    m14_rad = models.FloatField(db_column='M14_Rad', blank=True, null=True) # Field name made lowercase.
    m15_rad = models.FloatField(db_column='M15_Rad', blank=True, null=True) # Field name made lowercase.
    m16_rad = models.FloatField(db_column='M16_Rad', blank=True, null=True) # Field name made lowercase.
    solz_gmtco = models.FloatField(db_column='SOLZ_GMTCO', blank=True, null=True) # Field name made lowercase.
    sola_gmtco = models.FloatField(db_column='SOLA_GMTCO', blank=True, null=True) # Field name made lowercase.
    satz_gmtco = models.FloatField(db_column='SATZ_GMTCO', blank=True, null=True) # Field name made lowercase.
    sata_gmtco = models.FloatField(db_column='SATA_GMTCO', blank=True, null=True) # Field name made lowercase.
    scvx_gmtco = models.FloatField(db_column='SCVX_GMTCO', blank=True, null=True) # Field name made lowercase.
    scvy_gmtco = models.FloatField(db_column='SCVY_GMTCO', blank=True, null=True) # Field name made lowercase.
    scvz_gmtco = models.FloatField(db_column='SCVZ_GMTCO', blank=True, null=True) # Field name made lowercase.
    scpx_gmtco = models.FloatField(db_column='SCPX_GMTCO', blank=True, null=True) # Field name made lowercase.
    scpy_gmtco = models.FloatField(db_column='SCPY_GMTCO', blank=True, null=True) # Field name made lowercase.
    scpz_gmtco = models.FloatField(db_column='SCPZ_GMTCO', blank=True, null=True) # Field name made lowercase.
    scax_gmtco = models.FloatField(db_column='SCAX_GMTCO', blank=True, null=True) # Field name made lowercase.
    scay_gmtco = models.FloatField(db_column='SCAY_GMTCO', blank=True, null=True) # Field name made lowercase.
    scaz_gmtco = models.FloatField(db_column='SCAZ_GMTCO', blank=True, null=True) # Field name made lowercase.
    qf1_gmtco = models.BigIntegerField(db_column='QF1_GMTCO', blank=True, null=True) # Field name made lowercase.
    qf2_gmtco = models.BigIntegerField(db_column='QF2_GMTCO', blank=True, null=True) # Field name made lowercase.
    qf1_iicmo = models.BigIntegerField(db_column='QF1_IICMO', blank=True, null=True) # Field name made lowercase.
    qf2_iicmo = models.BigIntegerField(db_column='QF2_IICMO', blank=True, null=True) # Field name made lowercase.
    qf3_iicmo = models.BigIntegerField(db_column='QF3_IICMO', blank=True, null=True) # Field name made lowercase.
    qf4_iicmo = models.BigIntegerField(db_column='QF4_IICMO', blank=True, null=True) # Field name made lowercase.
    qf5_iicmo = models.BigIntegerField(db_column='QF5_IICMO', blank=True, null=True) # Field name made lowercase.
    qf6_iicmo = models.BigIntegerField(db_column='QF6_IICMO', blank=True, null=True) # Field name made lowercase.
    date_mscan = models.DateTimeField(db_column='Date_Mscan', blank=True, null=True) # Field name made lowercase.
    m10_center = models.BigIntegerField(db_column='M10_Center', blank=True, null=True) # Field name made lowercase.
    m10_avg = models.FloatField(db_column='M10_Avg', blank=True, null=True) # Field name made lowercase.
    m10_std = models.FloatField(db_column='M10_Std', blank=True, null=True) # Field name made lowercase.
    m10_nsigma = models.BigIntegerField(db_column='M10_Nsigma', blank=True, null=True) # Field name made lowercase.
    m10_dn = models.BigIntegerField(db_column='M10_DN', blank=True, null=True) # Field name made lowercase.
    m10_sample = models.BigIntegerField(db_column='M10_Sample', blank=True, null=True) # Field name made lowercase.
    m10_line = models.BigIntegerField(db_column='M10_Line', blank=True, null=True) # Field name made lowercase.
    m10_file = models.CharField(db_column='M10_File', max_length=120, blank=True) # Field name made lowercase.
    proc_date = models.DateTimeField(db_column='Proc_Date', blank=True, null=True) # Field name made lowercase.
    dnb_sample = models.BigIntegerField(db_column='DNB_Sample', blank=True, null=True) # Field name made lowercase.
    dnb_line = models.BigIntegerField(db_column='DNB_Line', blank=True, null=True) # Field name made lowercase.
    dnb_lat = models.FloatField(db_column='DNB_Lat', blank=True, null=True) # Field name made lowercase.
    dnb_lon = models.FloatField(db_column='DNB_Lon', blank=True, null=True) # Field name made lowercase.
    dnb_rad = models.FloatField(db_column='DNB_Rad', blank=True, null=True) # Field name made lowercase.
    dnb_dist = models.FloatField(db_column='DNB_Dist', blank=True, null=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'Nightfire_record'

class Nrcanalysis(models.Model):
    reportnum = models.IntegerField(primary_key=True)
    sheen_length = models.FloatField(blank=True, null=True)
    sheen_width = models.FloatField(blank=True, null=True)
    reported_spill_volume = models.FloatField(blank=True, null=True)
    min_spill_volume = models.FloatField(blank=True, null=True)
    calltype = models.CharField(max_length=20, blank=True)
    severity = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=20, blank=True)
    release_type = models.CharField(max_length=20, blank=True)
    class Meta:
        managed = False
        db_table = 'NrcAnalysis'

class Nrcgeocode(models.Model):
    reportnum = models.IntegerField()
    source = models.CharField(max_length=16)
    lat = models.FloatField()
    lng = models.FloatField()
    precision = models.DecimalField(max_digits=16, decimal_places=0)
    class Meta:
        managed = False
        db_table = 'NrcGeocode'

class Nrcmaterials(models.Model):
    # id = models.IntegerField(primary_key=True)
    pattern = models.CharField(max_length=32)
    group_label = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'NrcMaterials'

class Nrcparsedreport(models.Model):
    reportnum = models.IntegerField(primary_key=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    areaid = models.CharField(max_length=32, blank=True)
    blockid = models.CharField(max_length=32, blank=True)
    zip = models.CharField(max_length=16, blank=True)
    platform_letter = models.CharField(max_length=16, blank=True)
    sheen_size_length = models.CharField(max_length=16, blank=True)
    sheen_size_width = models.CharField(max_length=16, blank=True)
    affected_area = models.CharField(max_length=32, blank=True)
    county = models.CharField(max_length=32, blank=True)
    time_stamp = models.DateTimeField()
    ft_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'NrcParsedReport'

class Nrcreleaseincidents(models.Model):
    reportnum = models.IntegerField(blank=True, null=True)
    calltype = models.CharField(max_length=16, blank=True)
    recieved_datetime = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    incident_datetime = models.DateTimeField(blank=True, null=True)
    incidenttype = models.CharField(max_length=32, blank=True)
    cause = models.CharField(max_length=32, blank=True)
    location = models.TextField(blank=True)
    state = models.CharField(max_length=255, blank=True)
    nearestcity = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=255, blank=True)
    suspected_responsible_company = models.CharField(max_length=255, blank=True)
    medium_affected = models.CharField(max_length=255, blank=True)
    material_name = models.CharField(max_length=255, blank=True)
    full_report_url = models.CharField(max_length=255, blank=True)
    materials_url = models.CharField(max_length=255, blank=True)
    sheen_length = models.FloatField(blank=True, null=True)
    sheen_width = models.FloatField(blank=True, null=True)
    reported_spill_volume = models.FloatField(blank=True, null=True)
    min_spill_volume = models.FloatField(blank=True, null=True)
    severity = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=20, blank=True)
    release_type = models.CharField(max_length=20, blank=True)
    areaid = models.CharField(max_length=32, blank=True)
    blockid = models.CharField(max_length=32, blank=True)
    platform_letter = models.CharField(max_length=16, blank=True)
    zip = models.CharField(max_length=16, blank=True)
    affected_area = models.CharField(max_length=32, blank=True)
    geocode_source = models.CharField(max_length=16, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'NrcReleaseIncidents'

class Nrcscrapedfullreport(models.Model):
    reportnum = models.IntegerField(primary_key=True)
    full_report_body = models.TextField(blank=True)
    full_report_url = models.CharField(max_length=255, blank=True)
    parsed_blockid = models.CharField(max_length=32, blank=True)
    parsed_areaid = models.CharField(max_length=32, blank=True)
    parsed_latitude = models.CharField(max_length=32, blank=True)
    parsed_longitude = models.CharField(max_length=32, blank=True)
    class Meta:
        managed = False
        db_table = 'NrcScrapedFullReport'

class Nrcscrapedmaterial(models.Model):
    reportnum = models.IntegerField()
    chris_code = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=32)
    amount = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=32, blank=True)
    reached_water = models.CharField(max_length=16, blank=True)
    amt_in_water = models.FloatField(blank=True, null=True)
    amt_in_water_unit = models.CharField(max_length=32, blank=True)
    ft_id = models.IntegerField(blank=True, null=True)
    st_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'NrcScrapedMaterial'

class Nrcscrapedreport(models.Model):
    reportnum = models.IntegerField(primary_key=True)
    calltype = models.CharField(max_length=16, blank=True)
    recieved_datetime = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    incident_datetime = models.DateTimeField(blank=True, null=True)
    incidenttype = models.CharField(max_length=32, blank=True)
    cause = models.CharField(max_length=32, blank=True)
    location = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    nearestcity = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=255, blank=True)
    suspected_responsible_company = models.CharField(max_length=255, blank=True)
    medium_affected = models.CharField(max_length=255, blank=True)
    material_name = models.CharField(max_length=255, blank=True)
    full_report_url = models.CharField(max_length=255, blank=True)
    materials_url = models.CharField(max_length=255, blank=True)
    time_stamp = models.DateTimeField()
    ft_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'NrcScrapedReport'

class Nrcscrapertarget(models.Model):
    # id = models.IntegerField(primary_key=True)
    done = models.BooleanField()
    execute_order = models.IntegerField(blank=True, null=True)
    startdate = models.DateTimeField(blank=True, null=True)
    enddate = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'NrcScraperTarget'

class Nrctag(models.Model):
    reportnum = models.IntegerField()
    tag = models.CharField(max_length=64)
    comment = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'NrcTag'

class Nrcunits(models.Model):
    # id = models.IntegerField(primary_key=True)
    unit_type = models.CharField(max_length=16)
    pattern = models.CharField(max_length=32)
    standardized_unit = models.CharField(max_length=32)
    conversion_factor = models.FloatField()
    class Meta:
        managed = False
        db_table = 'NrcUnits'

class PaDrillingpermit(models.Model):
    st_id = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    county_name = models.CharField(db_column='County_Name', max_length=20) # Field name made lowercase.
    municipality_name = models.CharField(db_column='Municipality_Name', max_length=20, blank=True) # Field name made lowercase.
    auth_id = models.IntegerField(db_column='Auth_Id', blank=True, null=True) # Field name made lowercase.
    date_disposed = models.DateField(db_column='Date_Disposed') # Field name made lowercase.
    disposition_code = models.CharField(db_column='Disposition_Code', max_length=20, blank=True) # Field name made lowercase.
    appl_type_code = models.CharField(db_column='Appl_Type_Code', max_length=20, blank=True) # Field name made lowercase.
    auth_type_description = models.CharField(db_column='Auth_Type_Description', max_length=60, blank=True) # Field name made lowercase.
    complete_api_field = models.CharField(db_column='Complete_API_', max_length=20) # Field name made lowercase. Field renamed because it ended with '_'.
    other_id = models.CharField(db_column='Other_Id', max_length=20) # Field name made lowercase.
    marcellus_shale_well = models.CharField(db_column='Marcellus_Shale_Well', max_length=4, blank=True) # Field name made lowercase.
    horizontal_well = models.CharField(db_column='Horizontal_Well', max_length=4, blank=True) # Field name made lowercase.
    well_type = models.CharField(db_column='Well_Type', max_length=20, blank=True) # Field name made lowercase.
    site_name = models.CharField(db_column='Site_Name', max_length=50, blank=True) # Field name made lowercase.
    total_depth = models.IntegerField(db_column='Total_Depth', blank=True, null=True) # Field name made lowercase.
    lat_deg = models.FloatField(db_column='Lat_Deg', blank=True, null=True) # Field name made lowercase.
    lat_min = models.FloatField(db_column='Lat_Min', blank=True, null=True) # Field name made lowercase.
    lat_sec = models.FloatField(db_column='Lat_Sec', blank=True, null=True) # Field name made lowercase.
    long_deg = models.FloatField(db_column='Long_Deg', blank=True, null=True) # Field name made lowercase.
    long_min = models.FloatField(db_column='Long_Min', blank=True, null=True) # Field name made lowercase.
    long_sec = models.FloatField(db_column='Long_Sec', blank=True, null=True) # Field name made lowercase.
    gis_datum = models.CharField(db_column='GIS_Datum', max_length=50, blank=True) # Field name made lowercase.
    latitude_decimal = models.FloatField(db_column='Latitude_Decimal', blank=True, null=True) # Field name made lowercase.
    longitude_decimal = models.FloatField(db_column='Longitude_Decimal', blank=True, null=True) # Field name made lowercase.
    client_id = models.IntegerField(db_column='Client_Id', blank=True, null=True) # Field name made lowercase.
    operator = models.CharField(db_column='Operator', max_length=100, blank=True) # Field name made lowercase.
    address1 = models.CharField(db_column='Address1', max_length=255, blank=True) # Field name made lowercase.
    address2 = models.CharField(db_column='Address2', max_length=255, blank=True) # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=30, blank=True) # Field name made lowercase.
    state_code = models.CharField(db_column='State_Code', max_length=20, blank=True) # Field name made lowercase.
    zip_code = models.CharField(db_column='Zip_Code', max_length=20, blank=True) # Field name made lowercase.
    unconventional = models.CharField(db_column='Unconventional', max_length=4, blank=True) # Field name made lowercase.
    ogo_num = models.CharField(db_column='OGO_Num', max_length=20, blank=True) # Field name made lowercase.
    facility_id = models.CharField(db_column='Facility_Id', max_length=20, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'PA_DrillingPermit'

class PaSpud(models.Model):
    st_id = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    well_api_field = models.CharField(db_column='Well_API__', max_length=20) # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    ogo_field = models.CharField(db_column='OGO__', max_length=20) # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    spud_date = models.DateField(db_column='SPUD_Date') # Field name made lowercase.
    county = models.CharField(db_column='County', max_length=20, blank=True) # Field name made lowercase.
    municipality = models.CharField(db_column='Municipality', max_length=20, blank=True) # Field name made lowercase.
    operator_s_name = models.CharField(db_column='Operator_s_Name', max_length=100, blank=True) # Field name made lowercase.
    farm_name = models.CharField(db_column='Farm_Name', max_length=50, blank=True) # Field name made lowercase.
    well_number = models.CharField(db_column='Well_Number', max_length=20, blank=True) # Field name made lowercase.
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True) # Field name made lowercase.
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True) # Field name made lowercase.
    marcellus_ind_field = models.CharField(db_column='Marcellus_Ind_', max_length=4, blank=True) # Field name made lowercase. Field renamed because it ended with '_'.
    horizontal_ind_field = models.CharField(db_column='Horizontal_Ind_', max_length=4, blank=True) # Field name made lowercase. Field renamed because it ended with '_'.
    creation_date = models.DateTimeField(db_column='Creation_Date', blank=True, null=True) # Field name made lowercase.
    created_by = models.CharField(db_column='Created_By', max_length=20, blank=True) # Field name made lowercase.
    modification_date = models.DateTimeField(db_column='Modification_Date', blank=True, null=True) # Field name made lowercase.
    modified_by = models.CharField(db_column='Modified_By', max_length=20, blank=True) # Field name made lowercase.
    well_type = models.CharField(db_column='Well_Type', max_length=20, blank=True) # Field name made lowercase.
    unconventional = models.CharField(db_column='Unconventional', max_length=4, blank=True) # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'PA_Spud'

class PaSpudCopy(models.Model):
    st_id = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    well_api_field = models.CharField(db_column='Well_API__', max_length=20) # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    ogo_field = models.CharField(db_column='OGO__', max_length=20) # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    spud_date = models.DateField(db_column='SPUD_Date') # Field name made lowercase.
    county = models.CharField(db_column='County', max_length=20, blank=True) # Field name made lowercase.
    municipality = models.CharField(db_column='Municipality', max_length=20, blank=True) # Field name made lowercase.
    operator_s_name = models.CharField(db_column='Operator_s_Name', max_length=100, blank=True) # Field name made lowercase.
    farm_name = models.CharField(db_column='Farm_Name', max_length=50, blank=True) # Field name made lowercase.
    well_number = models.CharField(db_column='Well_Number', max_length=20, blank=True) # Field name made lowercase.
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True) # Field name made lowercase.
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True) # Field name made lowercase.
    marcellus_ind_field = models.CharField(db_column='Marcellus_Ind_', max_length=4, blank=True) # Field name made lowercase. Field renamed because it ended with '_'.
    horizontal_ind_field = models.CharField(db_column='Horizontal_Ind_', max_length=4, blank=True) # Field name made lowercase. Field renamed because it ended with '_'.
    creation_date = models.DateTimeField(db_column='Creation_Date', blank=True, null=True) # Field name made lowercase.
    created_by = models.CharField(db_column='Created_By', max_length=20, blank=True) # Field name made lowercase.
    modification_date = models.DateTimeField(db_column='Modification_Date', blank=True, null=True) # Field name made lowercase.
    modified_by = models.CharField(db_column='Modified_By', max_length=20, blank=True) # Field name made lowercase.
    well_type = models.CharField(db_column='Well_Type', max_length=20, blank=True) # Field name made lowercase.
    unconventional = models.CharField(db_column='Unconventional', max_length=4, blank=True) # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'PA_Spud_copy'

class PaSpudNew(models.Model):
    st_id = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    well_api_field = models.CharField(db_column='Well_API__', max_length=20) # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    ogo_field = models.CharField(db_column='OGO__', max_length=20) # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    spud_date = models.DateField(db_column='SPUD_Date') # Field name made lowercase.
    county = models.CharField(db_column='County', max_length=20, blank=True) # Field name made lowercase.
    municipality = models.CharField(db_column='Municipality', max_length=20, blank=True) # Field name made lowercase.
    operator_s_name = models.CharField(db_column='Operator_s_Name', max_length=100, blank=True) # Field name made lowercase.
    farm_name = models.CharField(db_column='Farm_Name', max_length=50, blank=True) # Field name made lowercase.
    well_number = models.CharField(db_column='Well_Number', max_length=20, blank=True) # Field name made lowercase.
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True) # Field name made lowercase.
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True) # Field name made lowercase.
    marcellus_ind_field = models.CharField(db_column='Marcellus_Ind_', max_length=4, blank=True) # Field name made lowercase. Field renamed because it ended with '_'.
    horizontal_ind_field = models.CharField(db_column='Horizontal_Ind_', max_length=4, blank=True) # Field name made lowercase. Field renamed because it ended with '_'.
    creation_date = models.DateTimeField(db_column='Creation_Date', blank=True, null=True) # Field name made lowercase.
    created_by = models.CharField(db_column='Created_By', max_length=20, blank=True) # Field name made lowercase.
    modification_date = models.DateTimeField(db_column='Modification_Date', blank=True, null=True) # Field name made lowercase.
    modified_by = models.CharField(db_column='Modified_By', max_length=20, blank=True) # Field name made lowercase.
    well_type = models.CharField(db_column='Well_Type', max_length=20, blank=True) # Field name made lowercase.
    unconventional = models.CharField(db_column='Unconventional', max_length=4, blank=True) # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'PA_Spud_new'

class PaViolation(models.Model):
    st_id = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    inspectionid = models.IntegerField(db_column='InspectionID') # Field name made lowercase.
    violationid = models.IntegerField(db_column='ViolationID', unique=True) # Field name made lowercase.
    enforcementid = models.IntegerField(db_column='EnforcementID', blank=True, null=True) # Field name made lowercase.
    operator = models.CharField(db_column='Operator', max_length=100, blank=True) # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, blank=True) # Field name made lowercase.
    inspectiondate = models.DateField(db_column='InspectionDate', blank=True, null=True) # Field name made lowercase.
    inspectiontype = models.CharField(db_column='InspectionType', max_length=50, blank=True) # Field name made lowercase.
    permit_api = models.CharField(db_column='Permit_API', max_length=20, blank=True) # Field name made lowercase.
    ismarcellus = models.CharField(db_column='IsMarcellus', max_length=8, blank=True) # Field name made lowercase.
    inspectioncategory = models.CharField(db_column='InspectionCategory', max_length=50, blank=True) # Field name made lowercase.
    county = models.CharField(db_column='County', max_length=20, blank=True) # Field name made lowercase.
    municipality = models.CharField(db_column='Municipality', max_length=20, blank=True) # Field name made lowercase.
    inspectionresult = models.CharField(db_column='InspectionResult', max_length=255, blank=True) # Field name made lowercase.
    inspectioncomment = models.TextField(db_column='InspectionComment', blank=True) # Field name made lowercase.
    violationdate = models.DateField(db_column='ViolationDate', blank=True, null=True) # Field name made lowercase.
    violationcode = models.CharField(db_column='ViolationCode', max_length=255, blank=True) # Field name made lowercase.
    violationtype = models.CharField(db_column='ViolationType', max_length=100, blank=True) # Field name made lowercase.
    violationcomment = models.CharField(db_column='ViolationComment', max_length=255, blank=True) # Field name made lowercase.
    resolveddate = models.DateField(db_column='ResolvedDate', blank=True, null=True) # Field name made lowercase.
    enforcementcode = models.CharField(db_column='EnforcementCode', max_length=100, blank=True) # Field name made lowercase.
    penaltyfinalstatus = models.CharField(db_column='PenaltyFinalStatus', max_length=100, blank=True) # Field name made lowercase.
    penaltydatefinal = models.DateField(db_column='PenaltyDateFinal', blank=True, null=True) # Field name made lowercase.
    enforcementdatefinal = models.DateField(db_column='EnforcementDateFinal', blank=True, null=True) # Field name made lowercase.
    penaltyamount = models.FloatField(db_column='PenaltyAmount', blank=True, null=True) # Field name made lowercase.
    totalamountcollected = models.FloatField(db_column='TotalAmountCollected', blank=True, null=True) # Field name made lowercase.
    unconventional = models.CharField(db_column='Unconventional', max_length=4, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'PA_Violation'

class Pacounty201101(models.Model):
    gid = models.IntegerField(primary_key=True)
    mslink = models.FloatField(db_column='MSLINK', blank=True, null=True) # Field name made lowercase.
    county_nam = models.CharField(db_column='COUNTY_NAM', max_length=15, blank=True) # Field name made lowercase.
    county_num = models.CharField(db_column='COUNTY_NUM', max_length=2, blank=True) # Field name made lowercase.
    fips_count = models.CharField(db_column='FIPS_COUNT', max_length=3, blank=True) # Field name made lowercase.
    county_are = models.FloatField(db_column='COUNTY_ARE', blank=True, null=True) # Field name made lowercase.
    county_per = models.FloatField(db_column='COUNTY_PER', blank=True, null=True) # Field name made lowercase.
    numeric_la = models.FloatField(db_column='NUMERIC_LA', blank=True, null=True) # Field name made lowercase.
    county_nu1 = models.FloatField(db_column='COUNTY_NU1', blank=True, null=True) # Field name made lowercase.
    area_sq_mi = models.FloatField(db_column='AREA_SQ_MI', blank=True, null=True) # Field name made lowercase.
    sound = models.CharField(db_column='SOUND', max_length=255, blank=True) # Field name made lowercase.
    spread_she = models.CharField(db_column='SPREAD_SHE', max_length=255, blank=True) # Field name made lowercase.
    image_name = models.CharField(db_column='IMAGE_NAME', max_length=255, blank=True) # Field name made lowercase.
    note_file = models.CharField(db_column='NOTE_FILE', max_length=255, blank=True) # Field name made lowercase.
    video = models.CharField(db_column='VIDEO', max_length=20, blank=True) # Field name made lowercase.
    district_n = models.CharField(db_column='DISTRICT_N', max_length=2, blank=True) # Field name made lowercase.
    pa_cty_cod = models.CharField(db_column='PA_CTY_COD', max_length=2, blank=True) # Field name made lowercase.
    maint_cty_field = models.CharField(db_column='MAINT_CTY_', max_length=1, blank=True) # Field name made lowercase. Field renamed because it ended with '_'.
    district_o = models.CharField(db_column='DISTRICT_O', max_length=4, blank=True) # Field name made lowercase.
    the_geom = models.GeometryField(srid=-1, blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'PaCounty2011_01'

class Pastate201101(models.Model):
    gid = models.IntegerField(primary_key=True)
    mslink = models.FloatField(db_column='MSLINK', blank=True, null=True) # Field name made lowercase.
    state_id = models.IntegerField(db_column='STATE_ID', blank=True, null=True) # Field name made lowercase.
    the_geom = models.PolygonField(srid=-1, blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'PaState2011_01'

class Publishedfeeditems(models.Model):
    # id = models.IntegerField(primary_key=True)
    task_id = models.IntegerField()
    feed_item_id = models.CharField(max_length=36)
    published = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'PublishedFeedItems'

class RssemailsubscriptionBackup(models.Model):
    # id = models.CharField(max_length=36)
    confirmed = models.SmallIntegerField()
    email = models.CharField(max_length=255)
    rss_url = models.CharField(max_length=255)
    interval_hours = models.IntegerField()
    last_email_sent = models.DateTimeField(blank=True, null=True)
    last_item_updated = models.DateTimeField(blank=True, null=True)
    lat1 = models.FloatField(blank=True, null=True)
    lat2 = models.FloatField(blank=True, null=True)
    lng1 = models.FloatField(blank=True, null=True)
    lng2 = models.FloatField(blank=True, null=True)
    last_update_sent = models.DateTimeField(blank=True, null=True)
    active = models.SmallIntegerField()
    name = models.CharField(max_length=30, blank=True)
    class Meta:
        managed = False
        db_table = 'RSSEmailSubscription_backup'

class Rssfeed(models.Model):
    # id = models.IntegerField(primary_key=True)
    url = models.CharField(max_length=255)
    last_read = models.DateTimeField()
    update_interval_secs = models.IntegerField()
    tag = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=32, blank=True)
    source_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'RssFeed'

class Rssfeeditem(models.Model):
    item_id = models.CharField(primary_key=True, max_length=255)
    content = models.BinaryField(blank=True, null=True)
    feed_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'RssFeedItem'

class RssfeeditemBackup(models.Model):
    item_id = models.CharField(max_length=255, blank=True)
    content = models.BinaryField(blank=True, null=True)
    feed_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'RssFeedItem_Backup'

class TempPgids(models.Model):
    # id = models.CharField(max_length=36, blank=True)
    class Meta:
        managed = False
        db_table = 'TEMP_PGIDS'

class Test(models.Model):
    # id = models.IntegerField(blank=True, null=True)
    url = models.CharField(max_length=255, blank=True)
    last_read = models.DateTimeField(blank=True, null=True)
    update_interval_secs = models.IntegerField(blank=True, null=True)
    tag = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=32, blank=True)
    source_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'TEST'

class Test2(models.Model):
    reportnum = models.IntegerField(blank=True, null=True)
    calltype = models.CharField(max_length=16, blank=True)
    recieved_datetime = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    incident_datetime = models.DateTimeField(blank=True, null=True)
    incidenttype = models.CharField(max_length=32, blank=True)
    cause = models.CharField(max_length=32, blank=True)
    location = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    nearestcity = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=255, blank=True)
    suspected_responsible_company = models.CharField(max_length=255, blank=True)
    medium_affected = models.CharField(max_length=255, blank=True)
    material_name = models.CharField(max_length=255, blank=True)
    full_report_url = models.CharField(max_length=255, blank=True)
    materials_url = models.CharField(max_length=255, blank=True)
    sheen_length = models.FloatField(blank=True, null=True)
    sheen_width = models.FloatField(blank=True, null=True)
    reported_spill_volume = models.FloatField(blank=True, null=True)
    min_spill_volume = models.FloatField(blank=True, null=True)
    severity = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=20, blank=True)
    release_type = models.CharField(max_length=20, blank=True)
    areaid = models.CharField(max_length=32, blank=True)
    blockid = models.CharField(max_length=32, blank=True)
    platform_letter = models.CharField(max_length=16, blank=True)
    zip = models.CharField(max_length=16, blank=True)
    affected_area = models.CharField(max_length=32, blank=True)
    geocode_source = models.CharField(max_length=16, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'TEST2'

class Wvcounty200503(models.Model):
    gid = models.IntegerField(primary_key=True)
    area = models.FloatField(db_column='AREA', blank=True, null=True) # Field name made lowercase.
    perimeter = models.FloatField(db_column='PERIMETER', blank=True, null=True) # Field name made lowercase.
    dep_24k_field = models.IntegerField(db_column='DEP_24K_', blank=True, null=True) # Field name made lowercase. Field renamed because it ended with '_'.
    dep_24k_id = models.IntegerField(db_column='DEP_24K_ID', blank=True, null=True) # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=15, blank=True) # Field name made lowercase.
    state = models.IntegerField(db_column='STATE', blank=True, null=True) # Field name made lowercase.
    fips = models.IntegerField(db_column='FIPS', blank=True, null=True) # Field name made lowercase.
    pop1986 = models.IntegerField(db_column='POP1986', blank=True, null=True) # Field name made lowercase.
    pop2000 = models.IntegerField(db_column='POP2000', blank=True, null=True) # Field name made lowercase.
    pop_chng = models.IntegerField(db_column='POP_CHNG', blank=True, null=True) # Field name made lowercase.
    popch_pct = models.FloatField(db_column='POPCH_PCT', blank=True, null=True) # Field name made lowercase.
    males = models.IntegerField(db_column='MALES', blank=True, null=True) # Field name made lowercase.
    females = models.IntegerField(db_column='FEMALES', blank=True, null=True) # Field name made lowercase.
    amer_ind = models.IntegerField(db_column='AMER_IND', blank=True, null=True) # Field name made lowercase.
    asian = models.IntegerField(db_column='ASIAN', blank=True, null=True) # Field name made lowercase.
    black = models.IntegerField(db_column='BLACK', blank=True, null=True) # Field name made lowercase.
    hawn_pl = models.IntegerField(db_column='HAWN_PL', blank=True, null=True) # Field name made lowercase.
    hispanic = models.IntegerField(db_column='HISPANIC', blank=True, null=True) # Field name made lowercase.
    mult_race = models.IntegerField(db_column='MULT_RACE', blank=True, null=True) # Field name made lowercase.
    other = models.IntegerField(db_column='OTHER', blank=True, null=True) # Field name made lowercase.
    white = models.IntegerField(db_column='WHITE', blank=True, null=True) # Field name made lowercase.
    households = models.IntegerField(db_column='HOUSEHOLDS', blank=True, null=True) # Field name made lowercase.
    avg_hh_sz = models.FloatField(db_column='AVG_HH_SZ', blank=True, null=True) # Field name made lowercase.
    hse_units = models.IntegerField(db_column='HSE_UNITS', blank=True, null=True) # Field name made lowercase.
    owner_occ = models.IntegerField(db_column='OWNER_OCC', blank=True, null=True) # Field name made lowercase.
    renter_occ = models.IntegerField(db_column='RENTER_OCC', blank=True, null=True) # Field name made lowercase.
    vacant = models.IntegerField(db_column='VACANT', blank=True, null=True) # Field name made lowercase.
    the_geom = models.PolygonField(srid=0, blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'WVCounty2005_03'

class WvDrillingpermit(models.Model):
    st_id = models.IntegerField(primary_key=True)
    ft_id = models.IntegerField(blank=True, null=True)
    api = models.CharField(db_column='API', max_length=12) # Field name made lowercase.
    permit_number = models.IntegerField(blank=True, null=True)
    permit_type = models.CharField(max_length=20, blank=True)
    current_operator = models.CharField(max_length=100, blank=True)
    farm_name = models.CharField(max_length=100, blank=True)
    well_number = models.CharField(max_length=50, blank=True)
    permit_activity_type = models.CharField(max_length=50, blank=True)
    permit_activity_date = models.DateField(blank=True, null=True)
    utm_north = models.FloatField(blank=True, null=True)
    utm_east = models.FloatField(blank=True, null=True)
    datum = models.IntegerField(blank=True, null=True)
    county = models.CharField(max_length=20, blank=True)
    class Meta:
        managed = False
        db_table = 'WV_DrillingPermit'

class FeedentryBackup(models.Model):
    # id = models.CharField(max_length=36, blank=True)
    title = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    source_id = models.IntegerField(blank=True, null=True)
    kml_url = models.CharField(max_length=255, blank=True)
    incident_datetime = models.DateTimeField(blank=True, null=True)
    published = models.DateTimeField(blank=True, null=True)
    regions = models.TextField(blank=True) # This field type is a guess.
    tags = models.TextField(blank=True) # This field type is a guess.
    the_geom = models.GeometryField(srid=0, blank=True, null=True)
    source_item_id = models.IntegerField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'feedentry_backup'

class FeedentryEwn2(models.Model):
    # id = models.CharField(unique=True, max_length=36)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    lat = models.FloatField()
    lng = models.FloatField()
    source_id = models.IntegerField()
    kml_url = models.CharField(max_length=255, blank=True)
    incident_datetime = models.DateTimeField()
    published = models.DateTimeField(blank=True, null=True)
    regions = models.TextField(blank=True) # This field type is a guess.
    tags = models.TextField(blank=True) # This field type is a guess.
    the_geom = models.GeometryField(srid=0, blank=True, null=True)
    source_item_id = models.IntegerField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'feedentry_ewn2'

class Feedsource(models.Model):
    # id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32, blank=True)
    generator = models.CharField(max_length=16, blank=True)
    query = models.TextField(blank=True)
    template = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'feedsource'

class Region(models.Model):
    # id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256, blank=True)
    code = models.CharField(unique=True, max_length=20, blank=True)
    the_geom = models.GeometryField(srid=0, blank=True, null=True)
    kml = models.TextField(blank=True)
    simple_geom = models.GeometryField(srid=0, blank=True, null=True)
    src = models.CharField(max_length=128, blank=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'region'

class Satimage(models.Model):
    # id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    size_bytes = models.IntegerField(blank=True, null=True)
    geo_extent = models.GeometryField(srid=0, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, blank=True)
    source = models.CharField(max_length=20, blank=True)
    acquisition_date = models.DateTimeField()
    url = models.CharField(max_length=255, blank=True)
    duration = models.TextField(blank=True) # This field type is a guess.
    orbit = models.IntegerField(blank=True, null=True)
    priority = models.IntegerField()
    pass_field = models.CharField(db_column='pass', max_length=10, blank=True) # Field renamed because it was a Python reserved word.
    orbit_position = models.FloatField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'satimage'

class SatimageAoi(models.Model):
    # id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    the_geom = models.GeometryField(srid=0)
    begin_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'satimage_aoi'

class SatimagePublished(models.Model):
    # id = models.IntegerField()
    source_image = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    url = models.CharField(max_length=255)
    geo_extent = models.GeometryField(srid=0, blank=True, null=True)
    name = models.CharField(unique=True, max_length=100, blank=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'satimage_published'

class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True)
    auth_srid = models.IntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True)
    proj4text = models.CharField(max_length=2048, blank=True)
    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'

class TempFsuSarFootprints(models.Model):
    granulename = models.CharField(db_column='GranuleName', primary_key=True, max_length=32) # Field name made lowercase.
    imagedate = models.DateTimeField(db_column='ImageDate') # Field name made lowercase.
    lat1 = models.FloatField(db_column='Lat1') # Field name made lowercase.
    lat2 = models.FloatField(db_column='Lat2') # Field name made lowercase.
    lng1 = models.FloatField(db_column='Lng1') # Field name made lowercase.
    lng2 = models.FloatField(db_column='Lng2') # Field name made lowercase.
    imagedate1 = models.DateTimeField(db_column='ImageDate1') # Field name made lowercase.
    imagedate2 = models.DateTimeField(db_column='ImageDate2') # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'temp_FSU_SAR_FOOTPRINTS'

class TempMaterial(models.Model):
    # id = models.IntegerField(primary_key=True)
    reportnum = models.IntegerField()
    name = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'temp_material'

class TempNrcInSar(models.Model):
    reportnum = models.IntegerField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    granulename = models.CharField(db_column='granuleName', max_length=20, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'temp_nrc_in_sar'

class Tl2010UsState10(models.Model):
    gid = models.IntegerField(primary_key=True)
    region10 = models.CharField(db_column='REGION10', max_length=2, blank=True) # Field name made lowercase.
    division10 = models.CharField(db_column='DIVISION10', max_length=2, blank=True) # Field name made lowercase.
    statefp10 = models.CharField(db_column='STATEFP10', max_length=2, blank=True) # Field name made lowercase.
    statens10 = models.CharField(db_column='STATENS10', max_length=8, blank=True) # Field name made lowercase.
    geoid10 = models.CharField(db_column='GEOID10', max_length=2, blank=True) # Field name made lowercase.
    stusps10 = models.CharField(db_column='STUSPS10', max_length=2, blank=True) # Field name made lowercase.
    name10 = models.CharField(db_column='NAME10', max_length=100, blank=True) # Field name made lowercase.
    lsad10 = models.CharField(db_column='LSAD10', max_length=2, blank=True) # Field name made lowercase.
    mtfcc10 = models.CharField(db_column='MTFCC10', max_length=5, blank=True) # Field name made lowercase.
    funcstat10 = models.CharField(db_column='FUNCSTAT10', max_length=1, blank=True) # Field name made lowercase.
    aland10 = models.FloatField(db_column='ALAND10', blank=True, null=True) # Field name made lowercase.
    awater10 = models.FloatField(db_column='AWATER10', blank=True, null=True) # Field name made lowercase.
    intptlat10 = models.CharField(db_column='INTPTLAT10', max_length=11, blank=True) # Field name made lowercase.
    intptlon10 = models.CharField(db_column='INTPTLON10', max_length=12, blank=True) # Field name made lowercase.
    the_geom = models.GeometryField(srid=4269, blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'tl_2010_us_state10'

class Wvstateboundary100KUsgs200203Ll83(models.Model):
    gid = models.IntegerField(primary_key=True)
    area = models.FloatField(db_column='AREA', blank=True, null=True) # Field name made lowercase.
    state_name = models.CharField(db_column='STATE_NAME', max_length=25, blank=True) # Field name made lowercase.
    state_fips = models.CharField(db_column='STATE_FIPS', max_length=2, blank=True) # Field name made lowercase.
    sub_region = models.CharField(db_column='SUB_REGION', max_length=7, blank=True) # Field name made lowercase.
    state_abbr = models.CharField(db_column='STATE_ABBR', max_length=2, blank=True) # Field name made lowercase.
    pop1990 = models.IntegerField(db_column='POP1990', blank=True, null=True) # Field name made lowercase.
    pop1999 = models.IntegerField(db_column='POP1999', blank=True, null=True) # Field name made lowercase.
    pop90_sqmi = models.IntegerField(db_column='POP90_SQMI', blank=True, null=True) # Field name made lowercase.
    households = models.IntegerField(db_column='HOUSEHOLDS', blank=True, null=True) # Field name made lowercase.
    males = models.IntegerField(db_column='MALES', blank=True, null=True) # Field name made lowercase.
    females = models.IntegerField(db_column='FEMALES', blank=True, null=True) # Field name made lowercase.
    white = models.IntegerField(db_column='WHITE', blank=True, null=True) # Field name made lowercase.
    black = models.IntegerField(db_column='BLACK', blank=True, null=True) # Field name made lowercase.
    ameri_es = models.IntegerField(db_column='AMERI_ES', blank=True, null=True) # Field name made lowercase.
    asian_pi = models.IntegerField(db_column='ASIAN_PI', blank=True, null=True) # Field name made lowercase.
    other = models.IntegerField(db_column='OTHER', blank=True, null=True) # Field name made lowercase.
    hispanic = models.IntegerField(db_column='HISPANIC', blank=True, null=True) # Field name made lowercase.
    age_under5 = models.IntegerField(db_column='AGE_UNDER5', blank=True, null=True) # Field name made lowercase.
    age_5_17 = models.IntegerField(db_column='AGE_5_17', blank=True, null=True) # Field name made lowercase.
    age_18_29 = models.IntegerField(db_column='AGE_18_29', blank=True, null=True) # Field name made lowercase.
    age_30_49 = models.IntegerField(db_column='AGE_30_49', blank=True, null=True) # Field name made lowercase.
    age_50_64 = models.IntegerField(db_column='AGE_50_64', blank=True, null=True) # Field name made lowercase.
    age_65_up = models.IntegerField(db_column='AGE_65_UP', blank=True, null=True) # Field name made lowercase.
    nevermarry = models.IntegerField(db_column='NEVERMARRY', blank=True, null=True) # Field name made lowercase.
    married = models.IntegerField(db_column='MARRIED', blank=True, null=True) # Field name made lowercase.
    separated = models.IntegerField(db_column='SEPARATED', blank=True, null=True) # Field name made lowercase.
    widowed = models.IntegerField(db_column='WIDOWED', blank=True, null=True) # Field name made lowercase.
    divorced = models.IntegerField(db_column='DIVORCED', blank=True, null=True) # Field name made lowercase.
    hsehld_1_m = models.IntegerField(db_column='HSEHLD_1_M', blank=True, null=True) # Field name made lowercase.
    hsehld_1_f = models.IntegerField(db_column='HSEHLD_1_F', blank=True, null=True) # Field name made lowercase.
    marhh_chd = models.IntegerField(db_column='MARHH_CHD', blank=True, null=True) # Field name made lowercase.
    marhh_no_c = models.IntegerField(db_column='MARHH_NO_C', blank=True, null=True) # Field name made lowercase.
    mhh_child = models.IntegerField(db_column='MHH_CHILD', blank=True, null=True) # Field name made lowercase.
    fhh_child = models.IntegerField(db_column='FHH_CHILD', blank=True, null=True) # Field name made lowercase.
    hse_units = models.IntegerField(db_column='HSE_UNITS', blank=True, null=True) # Field name made lowercase.
    vacant = models.IntegerField(db_column='VACANT', blank=True, null=True) # Field name made lowercase.
    owner_occ = models.IntegerField(db_column='OWNER_OCC', blank=True, null=True) # Field name made lowercase.
    renter_occ = models.IntegerField(db_column='RENTER_OCC', blank=True, null=True) # Field name made lowercase.
    median_val = models.IntegerField(db_column='MEDIAN_VAL', blank=True, null=True) # Field name made lowercase.
    medianrent = models.IntegerField(db_column='MEDIANRENT', blank=True, null=True) # Field name made lowercase.
    units_1det = models.IntegerField(db_column='UNITS_1DET', blank=True, null=True) # Field name made lowercase.
    units_1att = models.IntegerField(db_column='UNITS_1ATT', blank=True, null=True) # Field name made lowercase.
    units2 = models.IntegerField(db_column='UNITS2', blank=True, null=True) # Field name made lowercase.
    units3_9 = models.IntegerField(db_column='UNITS3_9', blank=True, null=True) # Field name made lowercase.
    units10_49 = models.IntegerField(db_column='UNITS10_49', blank=True, null=True) # Field name made lowercase.
    units50_up = models.IntegerField(db_column='UNITS50_UP', blank=True, null=True) # Field name made lowercase.
    mobilehome = models.IntegerField(db_column='MOBILEHOME', blank=True, null=True) # Field name made lowercase.
    no_farms87 = models.IntegerField(db_column='NO_FARMS87', blank=True, null=True) # Field name made lowercase.
    avg_size87 = models.IntegerField(db_column='AVG_SIZE87', blank=True, null=True) # Field name made lowercase.
    crop_acr87 = models.IntegerField(db_column='CROP_ACR87', blank=True, null=True) # Field name made lowercase.
    avg_sale87 = models.IntegerField(db_column='AVG_SALE87', blank=True, null=True) # Field name made lowercase.
    the_geom = models.PolygonField(srid=-1, blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'wvStateBoundary100k_USGS_200203_ll83'

