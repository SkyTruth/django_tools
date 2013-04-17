import django.db
import django.core.management.base
import appomatic_mapdata.models
import optparse
import contextlib
import shapely.wkb
import shapely.wkt
import fastkml.kml
import fastkml.styles
import psycopg2
import optparse
import datetime
import csv
import os.path
import StringIO
import fastkml.config
import monkeypatches.fastkmlmonkey
import fcdjangoutils.sqlutils


KMLNS = '{http://www.opengis.net/kml/2.2}'

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))

def template_reports_mangle_row(columns, row):
    pass

def template_reports_name():
    return "Reports"

def template_reports_description():
    return 'All reports'

def template_cluster_mangle_row(columns, row):
    pass

def template_cluster_name(columns):
    return ""

def template_cluster_description(columns):
    columnnames = columns.keys()
    columnnames.sort()
    description = []
    for name in columnnames:
        t = columns[name]
        if name == 'id': continue
        if t == 'NUMBER':
            description.append('<tr><th>%s (min)</th><td>%%(%s_min)s' % (name, name))
            description.append('<tr><th>%s (max)</th><td>%%(%s_max)s' % (name, name))
            description.append('<tr><th>%s (avg)</th><td>%%(%s_avg)s' % (name, name))
            description.append('<tr><th>%s (stddev)</th><td>%%(%s_stddev)s' % (name, name))
        elif t == 'DATETIME':
            description.append('<tr><th>%s (min)</th><td>%%(%s_min)s' % (name, name))
            description.append('<tr><th>%s (max)</th><td>%%(%s_max)s' % (name, name))
            description.append('<tr><th>%s (avg)</th><td>%%(%s_avg)s' % (name, name))
            description.append('<tr><th>%s (stddev)</th><td>%%(%s_stddev)s' % (name, name))
    return '<h2>%(count)s</h2><table>' + ''.join(description) + '</table>'

def template_report_name(columns):
    return ""

def template_report_description(columns):
    columnnames = columns.keys()
    columnnames.sort()
    description = []
    for name in columnnames:
        if name == 'id': continue
        description.append('<tr><th>%s</th><td>%%(%s)s' % (name, name))
    return '<h2>%(id)s</h2><table>' + ''.join(description) + '</table>'

def sql_cluster_columns(columns):
    sqlcols = []
    for name, t in columns.iteritems():
        if name == 'id': continue
        if t == 'NUMBER':
            sqlcols.append('min(c."%s") as "%s_min"' % (name, name))
            sqlcols.append('max(c."%s") as "%s_max"' % (name, name))
            sqlcols.append('avg(c."%s") as "%s_avg"' % (name, name))
            sqlcols.append('stddev(c."%s") as "%s_stddev"' % (name, name))
        elif t == 'DATETIME':
            sqlcols.append('min(c."%s") as "%s_min"' % (name, name))
            sqlcols.append('max(c."%s") as "%s_max"' % (name, name))
            sqlcols.append('to_timestamp(avg(extract(\'epoch\' from c."%s"))) as "%s_avg"' % (name, name))
            sqlcols.append('stddev(extract(\'epoch\' from c."%s")) * interval \'1second\' as "%s_stddev"' % (name, name))
    return sqlcols

def get_color(value, minvalue = 0, maxvalue = 1, mincolor = (255, 00, 255, 255), maxcolor = (255, 00, 00, 255), nonecolor = (255, 00, 255, 255)):
    if value is None:
        color = nonecolor
    else:
        if maxvalue == minvalue:
            div = 1.0
        else:
            div = (value - minvalue) / (maxvalue - minvalue)
        if div < 0.0: div = 0.0
        if div > 1.0: div = 1.0
        color = tuple(c[1]*div + c[0]*(1.0-div)
                      for c in zip(mincolor, maxcolor))
    return "%02x%02x%02x%02x" % color


def extract_clusters(cur, query, size, radius, timeperiod):
    columns = fcdjangoutils.sqlutils.query_columns(cur, query)

    # Remove old data if any
    cur.execute("truncate table appomatic_mapcluster_cluster")

    #### Select the timeframe to work with
    filter = "true"
    args = {}
    if timeperiod is not None:
        filter = """
          datetime >= %(period_min)s and datetime <= %(period_max)s 
        """
        args["period_min"] = timeperiod[0]
        args["period_max"] = timeperiod[1]
    cur.execute("""
      insert into appomatic_mapcluster_cluster (
        reportnum, src, datetime, latitude, longitude, location, glocation)
      select
        id,
        src,
        datetime,
        latitude,
        longitude,
        location,
        location
      from
        """ + query + """ as a
      where
        """ + filter, args)

    # Create buffer
    # cur.execute("update appomatic_mapcluster_cluster set buffer = st_buffer(location, %(radius)s)", {"radius": radius})

    ### Compute score - all reports in buffer 
    ### Tack on the reportnum after the decimal place on the score
    ### so no two clusters will ever have the exact same score.
    ### This ensures that we don't get two overlapping clusters
    ### (with the same score, which would lead both of them to be
    ### included in the output)
    cur.execute("""
      update
        appomatic_mapcluster_cluster a
      set
        score = ((select
                    count(*) as c
                  from
                    appomatic_mapcluster_cluster b
                  where
                    ST_DWithin(a.glocation, b.glocation, %(radius)s))
                 || '.' || reportnum)::double precision
    """, {"radius": radius})

    ### Set max_score equal to the highest score in the buffer 
    cur.execute("""
      update
        appomatic_mapcluster_cluster a
      set
         max_score = (select
                        max(score) as c
                      from
                        appomatic_mapcluster_cluster b
                      where
                        ST_DWithin(a.glocation, b.glocation, %(radius)s))
    """, {"radius": radius})

    sqlcols = ["a.id",
               "floor(a.max_score) as count",
               "ST_Y(ST_Centroid(ST_Collect(b.location))) as latitude",
               "ST_X(ST_Centroid(ST_Collect(b.location))) as longitude",
               "ST_AsText(ST_Centroid(ST_Collect(b.location))) as shape"]
    sqlcols.extend(sql_cluster_columns(columns))
    sqlcols = ', '.join(sqlcols)

    cur.execute("""
      select
         min(floor(a.max_score)) as min,
         max(floor(a.max_score)) as max
       from  
         appomatic_mapcluster_cluster a
       where
         a.score = a.max_score
         and a.score >= %(size)s
    """, {"size": size})
    scoremin, scoremax = cur.next()

    result_sql = """
      select
         """ + sqlcols + """
       from  
         appomatic_mapcluster_cluster a
         join appomatic_mapcluster_cluster b on
           ST_DWithin(a.glocation, b.glocation, %(radius)s)
         join """ + query + """ as c on
           b.reportnum = c.id
       where
         a.score = a.max_score
         and a.score >= %(size)s
       group by
         a.id,
         a.max_score
       order by
         a.max_score desc
    """
    result_query = {"size": size, "radius": radius}

    colorcolumn = template_cluster_colorcolumn(columns)
    colors = template_cluster_colors(columns)
    cur.execute('''
      select
         min("''' + colorcolumn + '''") as min,
         max("''' + colorcolumn + '''") as max
       from  
         (''' + result_sql + ''') a
    ''', result_query)
    colormin, colormax = cur.next()

    cur.execute(result_sql, result_query)

    seq = 0
    for row in dictreader(cur):
	template_clusters_mangle_row(columns, row)
        yield {
            "seq": seq,
            "color": get_color(
                row[colorcolumn],
                colormin, colormax, **colors),
            "columns": columns,
            "scoremin": scoremin,
            "scoremax": scoremax,
            "description": template_cluster_description(columns),
            "name": template_cluster_name(columns),
            "row": row
            }
        seq += 1

def extract_reports(cur, query, periods):
    columns = fcdjangoutils.sqlutils.query_columns(cur, query)

    description = template_report_description(columns)
    name = template_report_name(columns)

    #### Select the timeframe to work with
    filter = "true"
    args = {}
    if periods:
        q = []
        for ind, timeperiod in enumerate(periods):
            q.append("datetime >= %%(period%s_min)s and datetime <= %%(period%s_max)s" % (ind, ind))
            args["period%s_min" % (ind,)] = timeperiod[0]
            args["period%s_max" % (ind,)] = timeperiod[1]
        filter = '(%s)' % ' or '.join(q)

    cur.execute("""
      select
        distinct grouping
      from
        """ + query + """ as a
      where
    """ + filter, args)
    groupings = [[row[0]] for row in cur]

    colorcolumn = template_reports_colorcolumn(columns)
    colors = template_reports_colors(columns)
    cur.execute('''
      select
         min("''' + colorcolumn + '''") as min,
         max("''' + colorcolumn + '''") as max
       from  
         ''' + query + ''' a
       where
    ''' + filter, args)
    colormin, colormax = cur.next()

    for grouping in groupings:
        def getRows():
            groupargs = {"grouping": grouping[0]}
            groupargs.update(args)
            cur.execute("""
              select
                *,
                ST_X(location) as longitude,
                ST_Y(location) as latitude,
                ST_AsText(location) as shape
              from
                """ + query + """ as a 
              where
                grouping = %(grouping)s and
            """ + filter, groupargs)

            seq = 0
            for row in dictreader(cur):
	        template_reports_mangle_row(columns, row)
                yield {'row': row,
                       'description': description,
                       'name': name,
                       "seq": seq,
                       "color": get_color(
                        row[colorcolumn],
                        colormin, colormax, **colors)}
                seq += 1
        grouping.append(getRows())
    return groupings


def extract_reports_kml(cur, query, periods, doc):
    folder = fastkml.kml.Folder(KMLNS, 'all-reports', template_reports_name(), template_reports_description())
    doc.append(folder)

    icons = [
        "http://maps.google.com/mapfiles/kml/shapes/open-diamond.png",
        "http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png",
        "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png",
        "http://maps.google.com/mapfiles/kml/shapes/placemark_square_highlight.png",
        "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png",
        "http://maps.google.com/mapfiles/kml/shapes/polygon.png",
        "http://maps.google.com/mapfiles/kml/shapes/star.png",
        "http://maps.google.com/mapfiles/kml/shapes/target.png",
        "http://maps.google.com/mapfiles/kml/shapes/triangle.png"]

    groupings = extract_reports(cur, query, periods)

    for ind, (typename, rows) in enumerate(groupings):
        subfolder = fastkml.kml.Folder(KMLNS, typename, typename)
        folder.append(subfolder)

        for info in rows:
            style = fastkml.styles.Style(KMLNS, "style-%s-%s-normal" % (typename, info["seq"],))
            style.append_style(fastkml.styles.IconStyle(
                    KMLNS,
                    "style-%s-%s-normal-icon" % (typename, info["seq"],),
                    scale=0.5,
                    icon_href=icons[ind % len(icons)],
                    color=info['color']))
            style.append_style(fastkml.styles.LabelStyle(
                    KMLNS,
                    "style-%s-%s-normal-label" % (typename, info["seq"],),
                    scale=0))
            doc.append_style(style)

            style = fastkml.styles.Style(KMLNS, "style-%s-%s-highlight" % (typename, info["seq"],))
            style.append_style(fastkml.styles.IconStyle(
                    KMLNS,
                    "style-%s-%s-highlight-icon" % (typename, info["seq"],),
                    scale=1.0,
                    icon_href=icons[ind % len(icons)],
                    color=info['color']))
            style.append_style(fastkml.styles.LabelStyle(
                    KMLNS,
                    "style-%s-%s-highlight-label" % (typename, info["seq"],),
                    scale=1))
            doc.append_style(style)

            style_map = fastkml.styles.StyleMap(
                KMLNS,
                "style-%s-%s" % (typename, info["seq"],))
            style_map.normal = fastkml.styles.StyleUrl(KMLNS, url="#style-%s-%s-normal" % (typename, info["seq"],))
            style_map.highlight = fastkml.styles.StyleUrl(KMLNS, url="#style-%s-%s-highlight" % (typename, info["seq"],))
            doc.append_style(style_map)

            placemark = fastkml.kml.Placemark(KMLNS, "%(id)s" % info['row'], info['name'] % info['row'], info['description'] % info['row'])
            placemark.geometry = shapely.wkt.loads(str(info['row']['shape']))
            placemark.styleUrl = "#style-%s-%s" % (typename, info["seq"],)
            subfolder.append(placemark)



def extract_clusters_kml(cur, query, size, radius, timeperiod, doc):
    timeperiodstr = "%s-%s" % (timeperiod[0].strftime("%Y-%m-%d"), timeperiod[1].strftime("%Y-%m-%d"))

    foldername = 'Clusters %s:%s' % (timeperiod[0].strftime("%Y-%m-%d"), timeperiod[1].strftime("%Y-%m-%d"))
    folder = fastkml.kml.Folder(KMLNS,
                                 django.template.defaultfilters.slugify(foldername),
                                foldername,
                                '')
    doc.append(folder)


    style = fastkml.styles.Style(KMLNS, "style-%s-normal" % (timeperiodstr,))
    style.append_style(fastkml.styles.IconStyle(
            KMLNS,
            "style-%s-normal-icon" % (timeperiodstr,),
            icon_href="http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png"))
    style.append_style(fastkml.styles.LabelStyle(
            KMLNS,
            "style-%s-normal-label" % (timeperiodstr,),
            scale=0))
    doc.append_style(style)

    style = fastkml.styles.Style(KMLNS, "style-%s-highlight" % (timeperiodstr,))
    style.append_style(fastkml.styles.IconStyle(
            KMLNS,
            "style-%s-highlight-icon" % (timeperiodstr,),
            icon_href="http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png"))
    style.append_style(fastkml.styles.LabelStyle(
            KMLNS,
            "style-%s-highlight-label" % (timeperiodstr,),
            scale=1))
    doc.append_style(style)

    style_map = fastkml.styles.StyleMap(
        KMLNS,
        "style-%s" % (timeperiodstr,))
    style_map.normal = fastkml.styles.StyleUrl(KMLNS, url="#style-%s-normal" % (timeperiodstr,))
    style_map.highlight = fastkml.styles.StyleUrl(KMLNS, url="#style-%s-highlight" % (timeperiodstr,))
    doc.append_style(style_map)


    for info in extract_clusters(cur, query, size, radius, timeperiod):
        if info['scoremax'] - info['scoremin']:
            scale = 0.5 + 2 * (float(info['row']['count'] - info['scoremin']) / (info['scoremax'] - info['scoremin']))
        else:
            scale = 1.0

        style = fastkml.styles.Style(KMLNS, "style-%s-%s-normal" % (timeperiodstr, info['seq']))
        style.append_style(fastkml.styles.IconStyle(
                KMLNS,
                "style-%s-%s-normal-icon" % (timeperiodstr, info['seq']),
                scale=scale,
                color=info['color']))
        doc.append_style(style)

        style = fastkml.styles.Style(KMLNS, "style-%s-%s-highlight" % (timeperiodstr, info['seq']))
        style.append_style(fastkml.styles.IconStyle(
                KMLNS,
                "style-%s-%s-highlight-icon" % (timeperiodstr, info['seq']),
                scale=scale + 1,
                color=info['color']))
        doc.append_style(style)

        style_map = fastkml.styles.StyleMap(
            KMLNS,
            "style-%s-%s" % (timeperiodstr, info['seq']))
        style_map.normal = fastkml.styles.StyleUrl(KMLNS, url="#style-%s-%s-normal" % (timeperiodstr, info['seq']))
        style_map.highlight = fastkml.styles.StyleUrl(KMLNS, url="#style-%s-%s-highlight" % (timeperiodstr, info['seq']))

        placemark = fastkml.kml.Placemark(KMLNS, "%s-%s" % (timeperiodstr, info['seq']), info['name'] % info['row'], info['description'] % info['row'])
        placemark.geometry = shapely.wkt.loads(str(info['row']['shape']))
        placemark.styleUrl = "#style-%s" % (timeperiodstr,)
        placemark.append_style(style_map)
        folder.append(placemark)


def extract_kml(name, cur, query, size, radius, periods):
    kml = fastkml.kml.KML()

    docname = name
    if periods:
        docname += ' ' + ', '.join("%s:%s" % (timeperiod[0].strftime("%Y-%m-%d"), timeperiod[1].strftime("%Y-%m-%d"))
                                   for timeperiod in periods)

    doc = fastkml.kml.Document(KMLNS, django.template.defaultfilters.slugify(docname), docname, '')
    kml.append(doc)

    for timeperiod in periods:
        extract_clusters_kml(cur, query, size, radius, timeperiod, doc)

    extract_reports_kml(cur, query, periods, doc)

    return kml.to_string(prettyprint=True)


def extract_clusters_csv(cur, query, radius, size, timeperiod, doc):
    global columns
    for info in extract_clusters(cur, query, radius, size, timeperiod):
        info['row']['periodstart'] = timeperiod[0]
        info['row']['periodend'] = timeperiod[1]
        del info['row']['shape']

        if columns is None:
            columns = info['row'].keys()
            columns.sort()
            doc.writerow(columns)

        doc.writerow([info['row'][col] for col in columns])

def extract_reports_csv(cur, query, periods, doc):
    global columns

    for (typename, rows) in extract_reports(cur, query, periods):
        for info in rows:
            del info['row']['shape']

            if columns is None:
                columns = info['row'].keys()
                columns.sort()
                doc.writerow(columns)

            doc.writerow([info['row'][col] for col in columns])

def extract_csv(name, cur, query, size, radius, periods, doc):
    global columns
    columns = None
    for timeperiod in periods:
        extract_clusters_csv(cur, query, size, radius, timeperiod, doc)

def extract_csv_reports(name, cur, query, size, radius, periods, doc):
    global columns
    columns = None
    extract_reports_csv(cur, query, periods, doc)

def decodePeriod(period):
    start, end = period.split(":")
    if start:
        start = datetime.datetime.strptime(start, '%Y-%m-%d')
    if end:
        end = datetime.datetime.strptime(end, '%Y-%m-%d')
    if not start:
        if not end:
            end = datetime.datetime.now()
        start = end - datetime.interval(30)
    if not end:
        end = start + datetime.interval(30)
    return (start, end)

def extract(name, query, template=None, format='kml', size = 4, radius=7500, periods = [], *args, **options):
    if template:
        with open(os.path.expanduser(template)) as f:
            exec f in globals()

    if periods:
        periods = [decodePeriod(period)
                   for period in periods]
    else:
        now = datetime.datetime.now()
        periods = [(now - datetime.timedelta(timeperiod), now)
                   for timeperiod in (12*30, 6*30, 3*30, 30)]

    with contextlib.closing(django.db.connection.cursor()) as cur:
        if format == 'kml':
            return extract_kml(name, cur, query, size, radius, periods).encode('utf-8')
        elif format == 'csv':
            f = StringIO.StringIO()
            extract_csv(name, cur, query, size, radius, periods, csv.writer(f))
            return f.getvalue()
        elif format == 'csv_reports':
            f = StringIO.StringIO()
            extract_csv_reports(name, cur, query, size, radius, periods, csv.writer(f))
            return f.getvalue()
        else:
            raise Exception("Unsupported format")
