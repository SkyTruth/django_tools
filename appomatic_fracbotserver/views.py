import fcdjangoutils.jsonview
import fcdjangoutils.cors
import django.db
from django.conf import settings
import appomatic_legacymodels.models
import appomatic_siteinfo.models
import appomatic_fracbotserver.models
import datetime
import django.core.exceptions
import pytz
import fracfocustools
import django.http
import django.views.decorators.csrf
import base64
import contextlib
import django.db
import re
import appomatic_siteinfo.management.commands.fracscrapeimport
import fcdjangoutils.sqlutils
import fcdjangoutils.date
import dateutil.parser
import os.path

PDFDIR = os.path.join(settings.MEDIA_ROOT, 'fracbot')
if not os.path.exists(PDFDIR):
    os.makedirs(PDFDIR)

def set_cookie(response, key, value, max_age = 365 * 24 * 60 * 60):
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(
        key, value, max_age=max_age, expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None)

def track_client(fn):
    def track_client(request, *arg, **kw):
        request.fracbotclient = None
        if 'fracbotclientid' in request.COOKIES:
            clients = appomatic_fracbotserver.models.Client.objects.filter(id = request.COOKIES['fracbotclientid'])
            if clients: request.fracbotclient = clients[0]
        if not request.fracbotclient:
            request.fracbotclient = appomatic_fracbotserver.models.Client(
                info = dict((key, value)
                            for key, value in request.META.iteritems()
                            if isinstance(value, (str, unicode))),
                ip = request.META.get('REMOTE_ADDR', ''),
                domain = request.META.get('REMOTE_HOST', ''),
                agent = request.META.get('HTTP_USER_AGENT', ''))
            request.fracbotclient.save()
        response = fn(request, *arg, **kw)
        if 'fracbotclientid' not in request.COOKIES:
            set_cookie(response, 'fracbotclientid', request.fracbotclient.id)
        return response
    return track_client

def log_activity(request, activity_type, amount=1, **info):
    existing = appomatic_fracbotserver.models.ActivityType.objects.filter(name=activity_type)
    if existing:
        activity_type = existing[0]
    else:
        activity_type = appomatic_fracbotserver.models.ActivityType(name=activity_type)
        activity_type.save()
    appomatic_fracbotserver.models.Activity(client=request.fracbotclient, type=activity_type, amount=amount, info=info).save()

def process_client_event(cur, info):
    data = info.get('data', {})
    event = data.get('event', None)
    key = data.get('key', None)
    if key and (event == 'TASKOK'):
        cur.execute("""UPDATE "FracFocusTask"
                       set scraped='{}', score=0.0 where seqid={};"""
                       .format(datetime.datetime.utcnow(), key)
                   )
        cur.execute('commit')

def logged_view(name, amount=1, **info):
    def logged_view(fn):
        def logged_view(request, *arg, **kw):
            try:
                return fn(request, *arg, **kw)
            except Exception, e:
                log_activity(request, "exception-%s" % name, amount=amount, error=e, **info)
                raise
        return logged_view
    return logged_view

def parseDate(date):
    """Parses dates in american format (mm/dd/yyyy) with optional 0-padding."""
    try:
        return datetime.date(*dateutil.parser.parse(date,fuzzy=1).timetuple()[:3])
    except:
        return None

def parseFloat(str):
    try:
        if not str: return None
        str = str.strip()
        if not str: return None
        return float(str.replace(',', ''))
    except:
        return None

def get(query):
    if query:
        return query[0]
    return None


def check_record(cur, row):
    api = row["API No."]
    jobdate = row["job_date"] = parseDate(row["Job Start Dt"])
    jobtime = datetime.datetime(jobdate.year, jobdate.month, jobdate.day).replace(tzinfo=pytz.utc)

    cur.execute("""select seqid from "FracFocusScrape" where api = %(api)s and job_date = %(jobdate)s""", {'api': api, 'jobdate':jobdate})
    for dbrow in cur:
        row['pdf_seqid'] = dbrow[0]
    if 'pdf_seqid' in row:

        # There really should be a bot status if we get here, but in case there isn't... fix it
        cur.execute("""select count(*) as existing from "BotTaskStatus" where task_id = %(pdf_seqid)s and bot = 'FracFocusReport'""",row)
        if not fcdjangoutils.sqlutils.dictreader(cur).next()['existing']:
            cur.execute("""insert into "BotTaskStatus" (task_id, bot, status) values (%(pdf_seqid)s, 'FracFocusReport', 'NEW')""", row)

    else:
        cur.execute("""insert into "FracFocusScrape" (api, job_date, state, county, operator, well_name, well_type, latitude, longitude, datum) values(%(API No.)s, %(job_date)s, %(State)s, %(County)s, %(Operator)s, %(WellName)s, NULL,%(Latitude)s, %(Longitude)s, %(Datum)s)""", row)
        cur.execute("select lastval()")
        row['pdf_seqid'] = cur.fetchone()[0]

        cur.execute("""insert into "BotTaskStatus" (task_id, bot, status) values(%(pdf_seqid)s, 'FracFocusReport', 'NEW')""", row)

        cur.execute("""
          update appomatic_fracbotserver_county as c
          set scrapepoints = c.scrapepoints + 1
          from appomatic_fracbotserver_state as s
          where
            c.name=%(County)s
            and c.state_id = s.id
            and s.name = %(State)s
        """, row);

    cur.execute("""select * from "FracFocusReport" where pdf_seqid = %(pdf_seqid)s""", row)
    for dbrow in fcdjangoutils.sqlutils.dictreader(cur):
        row['pdf_content'] = dbrow

    well = get(appomatic_siteinfo.models.Well.objects.filter(api = api))
    if well:
        row['well_guuid'] = well.guuid
        row['site_guuid'] = well.site.guuid
        event = get(appomatic_siteinfo.models.FracEvent.objects.filter(well = well, datetime = jobtime))
        if event:
            row['event_guuid'] = event.guuid
            row['operator_guuid'] = event.operator.guuid

    if 'operator_guuid' not in row:
        lookup_name = re.sub(r'[^a-zA-Z0-9][^a-zA-Z0-9]*', '%', row['Operator'].lower())
        aliases = appomatic_siteinfo.models.CompanyAlias.objects.all().extra(where=["name ilike %s"], params=[lookup_name])
        if aliases:
            row['operator_guuid'] = aliases[0].alias_for.guuid


@django.views.decorators.csrf.csrf_exempt
@fcdjangoutils.cors.cors
@track_client
@fcdjangoutils.jsonview.json_view
@logged_view("check")
def check_records(request):
    with contextlib.closing(django.db.connection.cursor()) as cur:
        try:
            rows = fcdjangoutils.jsonview.from_json(request.POST['records'])
            for row in rows:
                check_record(cur, row)

            new_rows = [{'API No.': row['API No.'], 'Job Start Dt': row['Job Start Dt'],
                         'State': row['State'], 'County': row['County']}
                        for row in rows
                        if 'event_guuid' not in row]
            log_activity(request, "check", len(new_rows), new_rows = new_rows)

            return rows
        except:
            cur.execute('rollback')
            raise
        else:
            cur.execute('commit')

@django.views.decorators.csrf.csrf_exempt
@fcdjangoutils.cors.cors
@track_client
@fcdjangoutils.jsonview.json_view
@logged_view("pdf")
def parse_pdf(request):
    with contextlib.closing(django.db.connection.cursor()) as cur:
        row = fcdjangoutils.jsonview.from_json(request.POST['row'])
        data = dict(row)

        check_record(cur, data)

        if 'pdf_content' in data: return data

        # This is stuff that really shouldn't happen, but if it does, we don't want to fail either...
        cur.execute("""delete from "BotTaskStatus" where task_id = %(pdf_seqid)s and bot in ('FracFocusPDFDownloader', 'FracFocusPDFParser')""", data)

        try:
            logger = fracfocustools.Logger()

            pdfdata = base64.decodestring(request.POST['pdf'])
            with open(os.path.join(PDFDIR, "%(API No.)s-%(job_date)s.pdf" % data), "w") as f:
                f.write(pdfdata)

            pdf = fracfocustools.FracFocusPDFParser(pdfdata, logger).parse_pdf()

            if not pdf:
                raise Exception("Unable to parse PDF:" + str(logger.messages))

            data.update({'fracture_date': None, 'state': None, 'county': None, 'operator': None, 'well_name': None, 'production_type': None, 'latitude': None, 'longitude': None, 'datum': None, 'true_vertical_depth': None, 'total_water_volume': None})

            data.update(pdf.report_data)
            data['chemicals'] = pdf.chemicals

            data['api'] = data['API No.']

            data['fracture_date'] = parseDate(data['fracture_date'])
            data['latitude'] = parseFloat(data['latitude'])
            data['longitude'] = parseFloat(data['longitude'])
            data['true_vertical_depth'] = parseFloat(data['true_vertical_depth'])
            data['total_water_volume'] = parseFloat(data['total_water_volume'])

            cur.execute("""insert into "FracFocusReport" (pdf_seqid, api, fracture_date, state, county, operator, well_name, production_type, latitude, longitude, datum, true_vertical_depth, total_water_volume) values (%(pdf_seqid)s, %(api)s, %(fracture_date)s, %(state)s, %(county)s, %(operator)s, %(well_name)s, %(production_type)s, %(latitude)s, %(longitude)s, %(datum)s, %(true_vertical_depth)s, %(total_water_volume)s)""", data)

            for rownr, chemical in enumerate(data['chemicals']):
                tmp = {'fracture_date': None, 'row': None, 'trade_name': None, 'supplier': None, 'purpose': None, 'ingredients': None, 'cas_number': None, 'additive_concentration': None, 'hf_fluid_concentration': None, 'comments': None, 'cas_type': None}
                tmp.update(data)
                tmp.update(chemical)
                tmp['row'] = rownr # Yes, the pdf parser seems to stuff this up on some pdfs... reusing row numbers...
                tmp['additive_concentration'] = parseFloat(tmp['additive_concentration'])
                tmp['hf_fluid_concentration'] = parseFloat(tmp['hf_fluid_concentration'])
                cur.execute("""insert into "FracFocusReportChemical" (pdf_seqid, api, fracture_date, row, trade_name, supplier, purpose, ingredients, cas_number, additive_concentration, hf_fluid_concentration, comments, cas_type) values (%(pdf_seqid)s, %(api)s, %(fracture_date)s, %(row)s, %(trade_name)s, %(supplier)s, %(purpose)s, %(ingredients)s, %(cas_number)s, %(additive_concentration)s, %(hf_fluid_concentration)s, %(comments)s, NULL)""", tmp)

            cur.execute("""update "BotTaskStatus" set status='DONE' where task_id=%(pdf_seqid)s and bot='FracFocusReport'""", data)
            cur.execute("""insert into "BotTaskStatus" (task_id, bot, status) values (%(pdf_seqid)s, 'FracFocusPDFDownloader', 'DONE')""", data)
            cur.execute("""insert into "BotTaskStatus" (task_id, bot, status) values (%(pdf_seqid)s, 'FracFocusPDFParser', 'DONE')""", data)

            log_activity(request, "pdf", state=data['state'], county=data['county'], api=data['api'], pdf_seqid=data['pdf_seqid'])

        except:
            cur.execute('rollback')
            raise
        else:
            cur.execute('commit')

        appomatic_siteinfo.management.commands.fracscrapeimport.scrapetoevent(
            appomatic_legacymodels.models.Fracfocusscrape.objects.get(seqid = data['pdf_seqid']),
            appomatic_legacymodels.models.Fracfocusreport.objects.get(pdf_seqid = data['pdf_seqid']),
            appomatic_siteinfo.models.Source.get("FracBot", ""))

        data = row
        check_record(cur, data)

        return data

@django.views.decorators.csrf.csrf_exempt
@fcdjangoutils.cors.cors
@track_client
@fcdjangoutils.jsonview.json_view
@logged_view("states")
def update_states(request):
    arg = fcdjangoutils.jsonview.from_json(request.POST['arg'])
    added = []
    for id, name in arg['states'].iteritems():
        existing = appomatic_fracbotserver.models.State.objects.filter(name=name)
        if not existing:
            appomatic_fracbotserver.models.State(name=name, siteid=id).save()
            added.append(name)
    if added:
        log_activity(request, "states", len(added), names=added)

@django.views.decorators.csrf.csrf_exempt
@fcdjangoutils.cors.cors
@track_client
@fcdjangoutils.jsonview.json_view
@logged_view("counties")
def update_counties(request):
    arg = fcdjangoutils.jsonview.from_json(request.POST['arg'])
    state = appomatic_fracbotserver.models.State.objects.get(name=arg['state'])
    added = []
    for id, name in arg['counties'].iteritems():
        existing = appomatic_fracbotserver.models.County.objects.filter(state=state, name=name)
        if not existing:
            appomatic_fracbotserver.models.County(state=state, name=name, siteid=id).save()
            added.append(name)
    if added:
        log_activity(request, "counties", len(added), state=arg['state'], names=added)

@django.views.decorators.csrf.csrf_exempt
@fcdjangoutils.cors.cors
@track_client
@fcdjangoutils.jsonview.json_view
def client_log(request):
    activity_type = request.POST['activity_type'] 
    info = fcdjangoutils.jsonview.from_json(request.POST['info'])
    log_activity(request, "client-" + activity_type, **info)
    if activity_type == 'fracbot_event':
        with contextlib.closing(django.db.connection.cursor()) as cur:
            process_client_event(cur, info)

@fcdjangoutils.cors.cors
@track_client
@fcdjangoutils.jsonview.json_view
@logged_view("task")
def get_task(request):
    with contextlib.closing(django.db.connection.cursor()) as cur:
        cur.execute("""
          with
            rand as
              (select random() * (select sum(scrapepoints) from appomatic_fracbotserver_county) as rand),
            counties as
              (select
                 *, sum(scrapepoints) over (order by id) randpos
               from appomatic_fracbotserver_county)
          select
            r.rand, c.randpos, c.id as county_id, s.id as state_id, c.name as county_name, s.name as state_name
          from
            counties c
            join rand r on
              r.rand >= c.randpos
            join appomatic_fracbotserver_state s on
              c.state_id = s.id
          order
            by c.randpos desc
          limit 1;
        """)
        task = fcdjangoutils.sqlutils.dictreader(cur).next()
        cur.execute("""update appomatic_fracbotserver_county set scrapepoints = scrapepoints * 0.9 where id = %(county_id)s""", task)
        return task

@fcdjangoutils.cors.cors
@track_client
@fcdjangoutils.jsonview.json_view
@logged_view("task2")
def get_task2(request):
    with contextlib.closing(django.db.connection.cursor()) as cur:
        cur.execute("""
                SELECT scraped from "FracFocusTask" where state_code='00';""")
        last_update, = cur.next()
        if (last_update is None or
            datetime.datetime.utcnow()-last_update > datetime.timedelta(days=1)
           ):
            update_fracfocustask_scores(cur)
        try:
            cur.execute("""SELECT seqid, score, records, scraped,
                           state_name, state_code, county_name, county_code
                           from "FracFocusTask"
                           where task_flag=1
                           order by score desc, random() limit 1;"""
                       )
            task = fcdjangoutils.sqlutils.dictreader(cur).next()
            cur.execute("""UPDATE "FracFocusTask"
                           set scraped='{}', score=-1.0 where seqid={};"""
                           .format(datetime.datetime.utcnow(), task['seqid'])
                       )
        except:
            cur.execute('rollback')
            raise
        else:
            cur.execute('commit')
        return task

def update_fracfocustask_scores(cur):
    try:
        # get api prefixs used in records search and as unique index
        cur.execute("""SELECT api_prefix from "FracFocusTask"
                       where task_flag=1;""")
        api_prefixes = list(cur)

        # set task record counts for last record interval
        for api_prefix, in api_prefixes:
            cur.execute("""UPDATE "FracFocusTask"
                           set records=(SELECT count(*) from "FracFocusScrape"
                                        where api like '{0}'||'%%'
                                          and age(job_date) < interval '1 year')
                           where api_prefix='{0}';""".format(api_prefix)
                           )

        # compute score
        cur.execute("""SELECT max(records) from "FracFocusTask"
                       where task_flag=1;""")
        max_records, = cur.next()
        cur.execute("""UPDATE "FracFocusTask"
                       set score=CASE
                          when scraped is NULL then 1.0
                          when score = -1.0 then 1.0
                          when age(scraped) < interval '7 days' then 0.0
                          when age(scraped) > interval '30 days' then 1.0
                          else greatest(date_part('day', age(scraped)) / 30.0,
                                        records::float / {})
                          END
                       where task_flag=1;""".format(max_records)
                   )
        cur.execute("""UPDATE "FracFocusTask"
                       set score=score*0.9
                       where task_flag=1 and records=0;""")

        cur.execute("""update "FracFocusTask" set scraped = '{}'
                       where state_code='00';"""
                    .format(datetime.datetime.utcnow())
                   )
    except:
        cur.execute('rollback')
        raise
    else:
        cur.execute('commit')

def statistics(request):
    return django.shortcuts.render(request, "appomatic_fracbotserver/statistics.html", {})

@fcdjangoutils.jsonview.json_view
def statistics_data(request):
    start, end = fcdjangoutils.date.decode_period(request.GET.get("period", "first() .. last()"))
    args = {
        "start": start,
        "end": end}

    with contextlib.closing(django.db.connection.cursor()) as cur:
        result = {"period": start.strftime("%Y-%m")}

        cur.execute("""
          select
            at.name, series date, coalesce(sum(a.amount), 0) amount
          from
            appomatic_fracbotserver_activitytype at
            join generate_series(%(start)s, %(end)s, interval '1 day') series on
              true
            left outer join appomatic_fracbotserver_activity a on
              a.type_id = at.id
              and a.datetime::date = series
          group by
            at.name, series
          order by
            at.name, series;
        """, args)
        activity = {}

        for row in fcdjangoutils.sqlutils.dictreader(cur):
            if row['name'] not in activity: activity[row['name']] = []
            activity[row['name']].append([row['date'], row['amount']])

        result['by_activity_and_date'] = [{"label": label, "values": values} for label, values in activity.iteritems()]



        cur.execute("""
          select
            c.ip, c.id, series date, coalesce(sum(a.amount),0) amount
          from
            appomatic_fracbotserver_client c
            join generate_series(%(start)s, %(end)s, interval '1 day') series on
              true
            left outer join appomatic_fracbotserver_activity a on
              a.client_id = c.id
              and a.datetime::date = series
          group by
            c.ip, c.id, series
          order by
            c.ip, c.id, series;
        """, args)
        activity = {}

        for row in fcdjangoutils.sqlutils.dictreader(cur):
            if row['ip'] not in activity: activity[row['ip']] = {}
            if row['id'] not in activity[row['ip']]: activity[row['ip']][row['id']] = []
            activity[row['ip']][row['id']].append([row['date'], row['amount']])

        activity_flattened = {}
        for ip, ids in activity.iteritems():
            for idx, (id, values) in enumerate(ids.iteritems()):
                activity_flattened["%s-%s" % (ip, idx)] = values

        result['by_client_and_date'] = [{"label": label, "values": values} for label, values in activity_flattened.iteritems()]

        return result
