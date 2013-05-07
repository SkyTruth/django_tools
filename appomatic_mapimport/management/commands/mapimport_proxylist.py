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
import parsedatetime

dateparser = parsedatetime.Calendar(parsedatetime.Constants())

logger = logging.getLogger(__name__)

class Command(appomatic_mapimport.seleniumimport.SeleniumImport):
    help = """Import fracfocusdata.org data
      Usage:
      xvfb-run -s "-screen scrn 1280x1280x24" appomatic mapimport_fracfocus 3 Texas Mitchell

      County and State are optional. You do want to specify screen-size (and set it that big) to avoid bugs in selenium.
    """
    SRC='FRACFOCUS'

    FIREFOX_PROFILEDIR = settings.MAPIMPORT_FRACFOCUS['PROFILE']

    baseurl = "http://hidemyass.com/proxy-list/"

    def get_proxies(self):
        self.connection.get(self.baseurl)
        self.wait_for_xpath("//*[@id='instructions']")
        while True:
            headers = [col.text.lower().replace(' ', '_')
                       for col in self.connection.find_elements_by_xpath("//table[@id='listtable']/thead/tr/td")]

            for row in self.connection.find_elements_by_xpath("//table[@id='listtable']/tbody/tr"):
                row = dict(zip(headers, [col.text for col in row.find_elements_by_xpath("./td")]))
                row['last_update'] = datetime.datetime(*dateparser.parse(row['last_update'])[0][:6])
                yield row

            nexts = self.connection.find_elements_by_xpath("//*[@class='nextpageactive']//*[@class='next']")
            if not nexts:
                break

            @appomatic_mapimport.mapimport.retry()
            def next():
                nexts[0].click()
                self.wait_for_xpath("//*[@id='instructions']")
                logger.debug("Loading one more page")

    def mapimport(self):
        for row in self.get_proxies():
            dbrows = appomatic_mapimport.models.Proxy.objects.filter(ip_address=row['ip_address'], port=row['port'])
            if dbrows:
                dbrow = dbrows[0]
            else:
                dbrow = appomatic_mapimport.models.Proxy()
            for key, value in row.iteritems():
                setattr(dbrow, key, value)
            dbrow.last_usage = datetime.datetime(1970, 1, 1)
            dbrow.save()
            logger.debug("Saved %(ip_address)s:%(port)s" % row)
