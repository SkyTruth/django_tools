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
import uuid

def dictreader(cur):
    for row in cur:
        yield dict(zip([col[0] for col in cur.description], row))

typeCodes = [(name, getattr(psycopg2, name))
             for name in ("Date",
                          "Time",
                          "Timestamp",
                          "DateFromTicks",
                          "TimeFromTicks",
                          "TimestampFromTicks",
                          "Binary",
                          "STRING",
                          "BINARY",
                          "NUMBER",
                          "DATETIME",
                          "ROWID")
             ] + [("Geometry", 456238)]

class Command(django.core.management.base.BaseCommand):
    help = 'Exports events as feed entries'
    args = '<source> [<query>]'

    option_list = django.core.management.base.BaseCommand.option_list + (
        optparse.make_option('--template',
            action='store',
            dest='template',
            default=None,
            help='Tempplate file for descriptions'),
        )

    def template_report(self, columns):
        templates = {}

        columnnames = columns.keys()
        columnnames.sort()
        columntable = []
        for name in columnnames:
            if name == 'id': continue
            columntable.append('<tr><th>%s</th><td>%%(%s)s' % (name, name))
        columntable = '<table>' + ''.join(columntable) + '</table>'

        templates['title'] = '%(id)s'
        templates['summary'] = columntable
        templates['content'] = columntable
        templates['link'] = ''
        templates['kml_url'] = ''
        templates['tags'] = '{}'

        return templates

    def sql_columns(self, columns):
        return ['a."%s"' % key for key in columns.keys()]

    def extract_columns(self, query):
        self.cur.execute("""
          select
            *
          from
            """ + query + """ as a
          limit 1
        """)

        return dict((name, ts[0])
                    for (name, ts) in ((column.name, 
                                        [name
                                         for name, t in typeCodes
                                         if column.type_code == t])
                                       for column in self.cur.description)
                    if ts)

    def extract_reports(self, sourceid, query):
        columns = self.extract_columns(query)

        templates = self.template_report(columns)
        sqlcolumns = ', '.join(self.sql_columns(columns))

        self.cur.execute("""
          select
            """ + sqlcolumns + """
          from
            """ + query + """ as a 
            left outer join feedentry as b on
              a.id = b.source_item_id
              and b.source_id = %(sourceid)s
          where
            b.id is null
        """, {"sourceid": sourceid})

        with contextlib.closing(django.db.connection.cursor()) as writecur:
            for row in dictreader(self.cur):
                row['entry_id'] = str(uuid.uuid4())
                row['source_id'] = sourceid
                for name, value in templates.iteritems():
                    row[name] = value % row

                writecur.execute("""
                  insert into feedentry (
                    id,
                    title,
                    link,
                    summary,
                    content,
                    lat,
                    lng,
                    source_id,
                    kml_url,
                    incident_datetime,
                    published,
                    regions,
                    tags,
                    the_geom,
                    source_item_id
                  ) select
                    %(entry_id)s,
                    %(title)s,
                    %(link)s,
                    %(summary)s,
                    %(content)s,
                    ST_Y(%(location)s),
                    ST_X(%(location)s),
                    %(source_id)s,
                    %(kml_url)s,
                    %(datetime)s,
                    now(),
                    (select array_agg(id) from region as r where st_contains(r.the_geom, %(location)s)),
                    %(tags)s,
                    %(location)s,
                    %(id)s
                """, row)

            writecur.execute("commit")

    def handle2(self, source, query = None, template=None, *args, **options):
        try:
            with contextlib.closing(django.db.connection.cursor()) as cur:
                self.cur = cur

                self.cur.execute("select count(*) from feedsource where generator = 'mapfeed' and name = %(name)s", {"name": source})
                if self.cur.next()[0] == 0:
                    self.cur.execute("insert into feedsource (id, name, generator, query, template) select (select max(id) + 1 from feedsource), %(name)s, 'mapfeed', %(query)s, %(template)s",
                                     {"name": source, "query": query, "template": template})
                else:
                    if template is None:
                        self.cur.execute("select template from feedsource where generator = 'mapfeed' and name = %(name)s", {"name": source})
                        for row in self.cur:
                            template = row[0]
                            break
                    else:
                        self.cur.execute("update feedsource set template = %(template)s where generator = 'mapfeed' and name = %(name)s", {"template": template, "name": source})

                    if query is None:
                        self.cur.execute("select query from feedsource where generator = 'mapfeed' and name = %(name)s", {"name": source})
                        for row in self.cur:
                            query = row[0]
                            break
                    else:
                        self.cur.execute("update feedsource set query = %(query)s where generator = 'mapfeed' and name = %(name)s", {"query": query, "name": source})

                self.cur.execute("select id from feedsource where generator = 'mapfeed' and name = %(name)s", {"name": source})
                sourceid = self.cur.next()[0]

                self.cur.execute("commit")

                if template:
                    with open(os.path.expanduser(template)) as f:
                        l = {}
                        exec f in l
                        for key, value in l.iteritems():
                            setattr(type(self), key, value) # hackety hack...

                self.extract_reports(sourceid, query)

        except Exception, e:
            print e
            import traceback
            traceback.print_exc()


    def handle(self, *args, **options):
        try:
            return self.handle2(*args, **options)
        except Exception, e:
            print type(e), e
            import traceback
            traceback.print_exc()
            raise
