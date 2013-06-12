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

    baseurl = "http://www.whatismyip.com"

    def mapimport(self):
        self.connection.get(self.baseurl)
        self.wait_for_xpath("//*[@id='greenip']")
        print self.connection.find_element_by_xpath("//*[@id='greenip']").text
        
