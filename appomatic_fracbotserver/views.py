import fcdjangoutils.jsonview
import django.db
from django.conf import settings
import appomatic_legacymodels.models
import appomatic_siteinfo.models
import datetime
import django.core.exceptions
import pytz

def parsedate(date):
    """Parses dates in american format (mm/dd/yyyy) with optional 0-padding."""
    month, day, year = [int(x.lstrip("0")) for x in date.split("/")]
    return datetime.date(year, month, day)

@fcdjangoutils.jsonview.json_view
def check_records(request):
    rows = fcdjangoutils.jsonview.from_json(request.GET['records'])
    for row in rows:
       api = row["API No."]
       jobdate = parsedate(row["Job Start Dt"])
       jobtime = datetime.datetime(jobdate.year, jobdate.month, jobdate.day).replace(tzinfo=pytz.utc)

       row['is_new'] = appomatic_legacymodels.models.Fracfocusscrape.objects.filter(api = api, job_date = jobdate).count() < 1

       try:
           well = appomatic_siteinfo.models.Well.objects.get(api = api)
           row['well_guuid'] = well.guuid
           row['site_guuid'] = well.site.guuid
           event = appomatic_siteinfo.models.FracEvent.objects.get(well = well, datetime = jobtime)
           row['event_guuid'] = event.guuid
           row['operator_guuid'] = event.operator.guuid
       except django.core.exceptions.ObjectDoesNotExist:
           pass
    return rows
