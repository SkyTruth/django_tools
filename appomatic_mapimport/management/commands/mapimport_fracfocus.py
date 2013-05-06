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
from django.conf import settings
import logging
import psycopg2

logger = logging.getLogger(__name__)

def retry(times=3):
    def retry(fn):
        def wrapper(*arg, **kw):
            for retry in xrange(0, times):
                try:
                    return fn(*arg, **kw)
                except Exception, e:
                    exc = e
                    logger.warn("Retrying %s. Failed due to: %s" % (fn.func_name, e))
                time.sleep(settings.MAPIMPORT_FRACFOCUS['THROTTLE'])
            raise exc
        return wrapper
    return retry


class Command(appomatic_mapimport.mapimport.Import):
    help = 'Import fracfocusdata.org data'
    SRC='FRACFOCUS'

    baseurl = "http://www.fracfocusdata.org/DisclosureSearch/StandardSearch.aspx"

    def wait_for_xpath(self, xpath, negate=False):
        """Waits for an xpath to match the document, or of negate is True, to not match any longer."""
        cond = selenium.webdriver.support.expected_conditions.presence_of_element_located(
            (selenium.webdriver.common.by.By.XPATH,
             xpath))
        wait = selenium.webdriver.support.ui.WebDriverWait(self.driver, 10)
        try:
            if negate:
                logger.debug("Waiting for %s to go away" % xpath)
                return wait.until_not(cond)
            else:
                logger.debug("Waiting for %s" % xpath)
                return wait.until(cond)
        except selenium.common.exceptions.TimeoutException, e:
            self.driver.get_screenshot_as_file('timeout-screenshot.png')
            if negate:
                raise Exception("%s never went away" % xpath)
            else:
                raise Exception("%s never showed up" % xpath)

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


    @retry()
    def get_states(self):
        self.driver.get(self.baseurl)
        time.sleep(settings.MAPIMPORT_FRACFOCUS['THROTTLE'])

        return dict(
            (state.text, state.get_attribute("value"))
            for state in self.driver.find_elements_by_xpath("//*[@id='MainContent_cboStateList']//option")
            if state.text != 'Choose a State')


    @retry()
    def get_counties(self, state = 'Texas'):
        self.driver.get(self.baseurl)
        time.sleep(settings.MAPIMPORT_FRACFOCUS['THROTTLE'])

        self.driver.find_element_by_xpath("//*[@id='MainContent_cboStateList']//*[text()='%s']" % state).click()

        self.wait_for_xpath("//*[@id='MainContent_cboCountyList']//*[text()='Choose a State First']", negate=True)

        return dict(
            (county.text, county.get_attribute("value"))
            for county in self.driver.find_elements_by_xpath("//*[@id='MainContent_cboCountyList']//option")
            if county.text != 'Choose a County')

    def get_file_from_record(self, element, row):
        pattern = os.path.join(settings.MAPIMPORT_FRACFOCUS['DOWNLOADDIR'], "*")

        @retry()
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

    def extract_records(self):
        # Wait for all of page to have loaded
        self.wait_for_xpath("//*[@id='lnkGroundWaterProtectionCouncil']")

        headers = [col.text
                   for col in self.driver.find_elements_by_xpath("//table[@id='MainContent_GridView1']//tr[th]"
                                                            )[0].find_elements_by_xpath(".//th")]

        for row in self.driver.find_elements_by_xpath("//table[@id='MainContent_GridView1']//tr[td]"):
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
    @retry()
    def get_records_for_county(self, state = 'Texas', county = 'Mitchell'):
        self.driver.get(self.baseurl)

        self.driver.find_element_by_xpath("//*[@id='MainContent_cboStateList']//*[text()='%s']" % state).click()
        self.wait_for_xpath("//*[@id='MainContent_cboCountyList']//*[text()='Choose a State First']", negate=True)
        self.driver.find_element_by_xpath("//*[@id='MainContent_cboCountyList']//*[text()='%s']" % county).click()

        self.driver.find_element_by_xpath("//*[@id='MainContent_btnSearch']").click()
        self.wait_for_xpath("//*[@id='MainContent_btnBackToFilter']")

        if not self.driver.find_elements_by_xpath("//td[contains(text(), 'any documents')]"):
            while True:
                current_page = self.driver.find_element_by_xpath("//*[@id='MainContent_GridView1_PageCurrent']").get_attribute("value")

                for record in self.extract_records():
                    yield record

                if not self.driver.find_elements_by_xpath("//*[@id='MainContent_GridView1_ButtonNext']"):
                    break

                logger.debug("Loading one more page of results for %(state)s / %(county)s" % {"state":state, "county":county})
                self.driver.find_element_by_xpath("//*[@id='MainContent_GridView1_ButtonNext']").click()
                self.wait_for_xpath("//*[@id='MainContent_GridView1_PageCurrent' and @value!='%s']" % current_page)

    def get_records(self, state=None, county=None):
        if state is None:
            states = self.get_states(self.driver).iterkeys()
        else:
            states = [state]
        for state in states:
            logger.debug("Getting record for %(state)s" % {"state":state})
            if county is None:
                counties = self.get_counties(state).iterkeys()
            else:
                counties = [county]
            for county in counties:
                logger.debug("Getting record for %(state)s / %(county)s" % {"state":state, "county":county})
                for record in self.get_records_for_county(state, county):
                    yield record


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


    def mapimport(self):
        self.driver = selenium.webdriver.Firefox(
            firefox_profile=selenium.webdriver.firefox.firefox_profile.FirefoxProfile(
                profile_directory=settings.MAPIMPORT_FRACFOCUS['PROFILE']))

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
