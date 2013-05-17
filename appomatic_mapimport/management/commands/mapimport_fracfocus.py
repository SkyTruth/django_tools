import selenium.webdriver
import selenium.common.exceptions
import selenium.webdriver.support.ui
import selenium.webdriver.support
import selenium.webdriver.support.expected_conditions
import selenium.webdriver.common.by
import selenium.common.exceptions
import glob
import time
import shutil
import os.path
import datetime
import appomatic_mapimport.mapimport
import appomatic_mapimport.seleniumimport
import appomatic_mapimport.models
from django.conf import settings
import logging
import psycopg2

logger = logging.getLogger(__name__)


class Command(appomatic_mapimport.seleniumimport.SeleniumImport):
    help = """Import fracfocusdata.org data
      Usage:
      xvfb-run -s "-screen scrn 1280x1280x24" appomatic mapimport_fracfocus 3 Texas Mitchell

      County and State are optional. You do want to specify screen-size (and set it that big) to avoid bugs in selenium.
    """
    SRC='FRACFOCUS'

    FIREFOX_PROFILEDIR = settings.MAPIMPORT_FRACFOCUS['PROFILE']

    baseurl = "http://www.fracfocusdata.org/DisclosureSearch/StandardSearch.aspx"

    def parsedate(self, date):
        """Parses dates in american format (mm/dd/yyyy) with optional 0-padding."""
        month, day, year = [int(x.lstrip("0")) for x in date.split("/")]
        return datetime.datetime(year, month, day)

    def clean_downloaddir(self):
        for item in glob.glob(os.path.join(settings.MAPIMPORT_FRACFOCUS['DOWNLOADDIR'], '*')):
            logger.debug("rm -rf %s" % item)
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.unlink(item)
        logger.debug("Cleaned the download dir")


    @appomatic_mapimport.mapimport.retryable()
    def get_states_from_site(self):
        self.connection.get(self.baseurl)
        time.sleep(settings.MAPIMPORT_FRACFOCUS['THROTTLE'])

        return dict(
            (state.text, state.get_attribute("value"))
            for state in self.connection.find_elements_by_xpath("//*[@id='MainContent_cboStateList']//option")
            if state.text != 'Choose a State')


    @appomatic_mapimport.mapimport.retryable()
    def get_counties_from_site(self, state):
        self.connection.get(self.baseurl)
        time.sleep(settings.MAPIMPORT_FRACFOCUS['THROTTLE'])

        self.connection.find_element_by_xpath("//*[@id='MainContent_cboStateList']//*[text()='%s']" % state).click()

        self.wait_for_xpath("//*[@id='MainContent_cboCountyList']//*[text()='Choose a State First']", negate=True)

        return dict(
            (county.text, county.get_attribute("value"))
            for county in self.connection.find_elements_by_xpath("//*[@id='MainContent_cboCountyList']//option")
            if county.text != 'Choose a County')

    def get_states(self):
        db_states = list(appomatic_mapimport.models.Downloaded.objects.filter(src=self.SRC, parent=None).order_by("-datetime"))
        db_states_dict = dict((obj.filename, obj) for obj in db_states)

        downloaded_states = self.get_states_from_site()

        for state in downloaded_states.iterkeys():
            if state not in db_states_dict:
                new_state = appomatic_mapimport.models.Downloaded(
                    src=self.SRC,
                    filename=state,
                    datetime=datetime.datetime(1970,1, 1))
                new_state.save()
                db_states.insert(0, new_state)

        return db_states

    def get_state(self, name):
        try:
            return appomatic_mapimport.models.Downloaded.objects.get(src=self.SRC, parent=None, filename=name)
        except:
            new_state = appomatic_mapimport.models.Downloaded(
                src=self.SRC,
                filename=name,
                datetime=datetime.datetime(1970,1, 1))
            new_state.save()
            return new_state

    def get_county(self, state, name):
        try:
            return appomatic_mapimport.models.Downloaded.objects.get(src=self.SRC, parent=state, filename=name)
        except:
            new_county = appomatic_mapimport.models.Downloaded(
                src=self.SRC,
                filename=name,
                parent = state,
                datetime=datetime.datetime(1970,1, 1))
            new_county.save()
            return new_county

    def get_counties(self, state):
        db_counties = list(appomatic_mapimport.models.Downloaded.objects.filter(src=self.SRC, parent=state).order_by("-datetime"))
        db_counties_dict = dict((obj.filename, obj) for obj in db_counties)

        downloaded_counties = self.get_counties_from_site(state.filename)

        for county in downloaded_counties.iterkeys():
            if county not in db_counties_dict:
                new_county = appomatic_mapimport.models.Downloaded(
                    parent=state,
                    src=self.SRC,
                    filename=county,
                    datetime=datetime.datetime(1970,1, 1))
                new_county.save()
                db_counties.insert(0, new_county)

        return db_counties

    def get_file_from_record(self, element, row):
        pattern = os.path.join(settings.MAPIMPORT_FRACFOCUS['DOWNLOADDIR'], "*")

        @appomatic_mapimport.mapimport.retryable()
        def attempt_download():
            if len(glob.glob(pattern)) > 0:
                logger.warn("Download dir not clean prior to download")
                self.clean_downloaddir()

            element.find_element_by_xpath(".//input").click()

            for wait in xrange(0, 60):
                logger.debug("Waiting for download")
                time.sleep(1)
                matches = glob.glob(pattern)
                if len(matches) == 1:
                    if os.stat(matches[0]).st_size > 0:
                        return matches[0]

            if len(glob.glob(pattern)) == 0:
                raise Exception("Download timed out")
            else:
                logger.warn("Download dir left in a terrible state. Doing what I can to clean up.")
                time.sleep(120)
                self.clean_downloaddir()
                raise Exception("Download stuffed up")

        try:
            src = attempt_download()
        except Exception, e:
            logger.warnt("No PDF downloadable for %(API No.)s @ %(Job Start Dt)s" % row)
        else:
            filename = "%s-%s: %s-%s @ %s.pdf" % (row['State'], row['County'], row['API No.'], row['WellName'], row['Job Start Dt'].strftime("%Y-%m-%d"))
            filename = filename.replace("/", "-")
            row['filename'] = filename
            row['path'] = os.path.join(self.dstdir, filename)
            os.rename(src, row['path'])
            logger.info("Downloaded PDF for %(API No.)s @ %(Job Start Dt)s" % row)

        if len(glob.glob(pattern)) > 0:
            self.clean_downloaddir()
            raise Exception("Download dir left in a terrible state. Doing what I can to clean up.")

    def is_new_record(self, record):
        self.cur.execute('''
          select
            count(*)
          from
            "FracFocusScrape"
          where
            api = %(API No.)s
            and job_date = %(Job Start Dt)s
        ''', record)
        return self.cur.next()[0] == 0

    def extract_records(self):
        # Wait for all of page to have loaded
        self.wait_for_xpath("//*[@id='lnkGroundWaterProtectionCouncil']")

        headers = [col.text
                   for col in self.connection.find_elements_by_xpath("//table[@id='MainContent_GridView1']//tr[th]"
                                                            )[0].find_elements_by_xpath(".//th")]

        for row in self.connection.find_elements_by_xpath("//table[@id='MainContent_GridView1']//tr[td]"):
            if len(row.find_elements_by_xpath(".//td")) != len(headers):
                logger.debug("Ignoring non-data row: %s", row.text)
                continue
            data = dict(zip(headers,
                           (item.text
                            for item in 
                            row.find_elements_by_xpath(".//td"))))
            data['Job Start Dt'] = self.parsedate(data['Job Start Dt'])
            data['Job End Dt'] = self.parsedate(data['Job End Dt'])
            data['Longitude'] = float(data['Longitude'])
            data['Latitude'] = float(data['Latitude'])
            logger.info("Scraped %(API No.)s @ %(Job Start Dt)s" % data)
            if self.is_new_record(data):
                self.get_file_from_record(row, data)
                if 'filename' in data:
                    yield data
            else:
                logger.debug("Ignoring old entry for %(API No.)s @ %(Job Start Dt)s" % data)

    # FIXME: Retry each page separately, and make sure the next-page button gets us to the right page...
    def get_records_for_county(self, state = 'Texas', county = 'Mitchell'):
        @appomatic_mapimport.mapimport.retry()
        def load_results():
            self.connection.get(self.baseurl)

            self.wait_for_xpath("//*[@id='MainContent_btnSearch']")

            self.connection.find_element_by_xpath("//*[@id='MainContent_cboStateList']//*[text()='%s']" % state).click()
            self.wait_for_xpath("//*[@id='MainContent_cboCountyList']//*[text()='Choose a State First']", negate=True)
            self.connection.find_element_by_xpath("//*[@id='MainContent_cboCountyList']//*[text()='%s']" % county).click()

            self.wait_for_xpath("//*[@id='MainContent_btnSearch']")
            self.connection.find_element_by_xpath("//*[@id='MainContent_btnSearch']").click()
            self.wait_for_xpath("//*[@id='MainContent_btnBackToFilter']")

        if not self.connection.find_elements_by_xpath("//td[contains(text(), 'any documents')]"):
            while True:
                current_page = self.connection.find_element_by_xpath("//*[@id='MainContent_GridView1_PageCurrent']").get_attribute("value")

                for record in self.extract_records():
                    yield record

                if not self.connection.find_elements_by_xpath("//*[@id='MainContent_GridView1_ButtonNext']"):
                    break

                @appomatic_mapimport.mapimport.retry
                def load_next():
                    logger.debug("Loading one more page of results for %(state)s / %(county)s" % {"state":state, "county":county})
                    self.connection.find_element_by_xpath("//*[@id='MainContent_GridView1_ButtonNext']").click()
                    self.wait_for_xpath("//*[@id='MainContent_GridView1_PageCurrent' and @value!='%s']" % current_page)

    def get_records(self, state=None, county=None):
        if state is None:
            states = self.get_states()
        else:
            states = [self.get_state(state)]
        for cur_state in states:
            logger.debug("Getting record for %(state)s" % {"state":cur_state.filename})
            if county is None:
                counties = self.get_counties(cur_state)
            else:
                counties = [self.get_county(cur_state, county)]
            for cur_county in counties:
                logger.debug("Getting record for %(state)s / %(county)s" % {"state":cur_state.filename, "county":cur_county.filename})
                for record in self.get_records_for_county(cur_state.filename, cur_county.filename):
                    yield record
                cur_county.save()
            cur_state.save()


    def mapimport(self):
        try:

            self.clean_downloaddir()

            for record in self.get_records(*self.args):
                self.cur.execute('''
                  insert into "FracFocusScrape" (
                    api,
                    job_date,
                    state,
                    county,
                    operator,
                    well_name,
                    well_type,
                    latitude,
                    longitude,
                    datum
                  ) values (
                    %(API No.)s,
                    %(Job Start Dt)s,
                    %(State)s,
                    %(County)s,
                    %(Operator)s,
                    %(WellName)s,
                    NULL,
                    %(Latitude)s,
                    %(Longitude)s,
                    %(Datum)s
                  )
                ''', record)
                self.cur.execute('select lastval()')
                record['task_id'] = self.cur.next()[0]

                self.cur.execute("""insert into "BotTaskStatus" (task_id, bot, status) values(%(task_id)s, 'FracFocusReport', 'NEW')""", record)

                with open(record['path']) as f:
                    record['data'] = psycopg2.Binary(f.read())

                self.cur.execute('''
                  insert into "FracFocusPDF" (
                    seqid,
                    pdf,
                    filename
                  ) select
                    %(task_id)s,
                    %(data)s,
                    %(filename)s
                ''', record)
                record['fileid'] = self.cur.lastrowid

                self.cur.execute("""insert into "BotTaskStatus" (task_id, bot, status) values(%(task_id)s, 'FracFocusPDFDownloader', 'DONE')""", record)

                self.cur.execute("commit")
                logger.info("Stored %(API No.)s @ %(Job Start Dt)s" % record)

                time.sleep(settings.MAPIMPORT_FRACFOCUS['THROTTLE'])

        except selenium.common.exceptions.TimeoutException, e:
            self.connection.get_screenshot_as_file('timeout-screenshot.png')
            raise
