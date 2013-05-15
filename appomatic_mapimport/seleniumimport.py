import selenium.webdriver
import selenium.common.exceptions
import selenium.webdriver.support.ui
import selenium.webdriver.support
import selenium.webdriver.support.expected_conditions
import selenium.webdriver.common.by
import selenium.common.exceptions
import selenium.webdriver.common.proxy
import appomatic_mapimport.mapimport
import appomatic_mapimport.models
import logging
import contextlib
import optparse

logger = logging.getLogger(__name__)

class SeleniumImport(appomatic_mapimport.mapimport.Import):
    option_list = appomatic_mapimport.mapimport.Import.option_list + (
        optparse.make_option('--no-proxy',
            action='store_false',
            dest='use_proxy',
            default=True,
            help='Do not use a proxy to connect'),
    )

    def wait_for_xpath(self, xpath, negate=False):
        """Waits for an xpath to match the document, or of negate is True, to not match any longer."""
        cond = selenium.webdriver.support.expected_conditions.presence_of_element_located(
            (selenium.webdriver.common.by.By.XPATH,
             xpath))
        wait = selenium.webdriver.support.ui.WebDriverWait(self.connection, 10)
        try:
            if negate:
                logger.debug("Waiting for %s to go away" % xpath)
                return wait.until_not(cond)
            else:
                logger.debug("Waiting for %s" % xpath)
                return wait.until(cond)
        except selenium.common.exceptions.TimeoutException, e:
            self.connection.get_screenshot_as_file('timeout-screenshot.png')
            if negate:
                raise Exception("%s never went away" % xpath)
            else:
                raise Exception("%s never showed up" % xpath)

    def proxyconf(self):
        if not self.kwargs['use_proxy']: return {}
        proxyconf = appomatic_mapimport.models.Proxy.get()
        proxyurl = "%s:%s" % (proxyconf.ip_address, proxyconf.port)
        logger.info("Using proxy %s" % proxyconf)
        return {"proxy": selenium.webdriver.common.proxy.Proxy({
                    'proxyType': selenium.webdriver.common.proxy.ProxyType.MANUAL,
                    'httpProxy': proxyurl,
                    'ftpProxy': proxyurl,
                    'sslProxy': proxyurl,
                    'noProxy': ''})}

    def profileconf(self):
        return {"firefox_profile": selenium.webdriver.firefox.firefox_profile.FirefoxProfile(
                profile_directory=self.FIREFOX_PROFILEDIR)}

    def connectionparams(self):
        res = {}
        res.update(self.profileconf())
        res.update(self.proxyconf())
        return res

    @contextlib.contextmanager
    def connect(self):
        @appomatic_mapimport.mapimport.retryable()
        def connect():
            self.connection = selenium.webdriver.Firefox(**self.connectionparams())
            self.connection.get("http://google.com")

        connect()
        logger.info("Connected")
        yield
