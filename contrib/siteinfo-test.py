from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class SiteinfoTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:8000"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_search_and_pages(self):
        driver = self.driver
        driver.get(self.base_url + "/siteinfo/search?query=water")
        driver.find_element_by_xpath("//em[normalize-space(.)='Chemical: Produced Water']").click()
        driver.find_element_by_link_text("COOPER 400 1H").click()
        driver.find_element_by_link_text("37-117-20326-00-00").click()
        driver.find_element_by_xpath("//em[normalize-space(.)='FracEvent: -77.066594E 41.932717N @ Jan. 3, 2011, 6 p.m.']").click()
        driver.find_element_by_link_text("Shell").click()
        driver.find_element_by_link_text("Carrier/Base Fluid").click()
        self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text, r"^[\s\S]*ChemicalPurpose: Carrier/Base Fluid[\s\S]*$")
        self.assertTrue(self.is_element_present(By.CSS_SELECTOR, "body.appomatic_siteinfo-models-ChemicalPurpose"))

    def test_pages(self):
        driver = self.driver
        driver.get(self.base_url + "/siteinfo/4adbdeec-ed0f-54f7-93bb-2dd1b6c4252f")
        driver.find_element_by_link_text("COOPER 400 1H").click()
        driver.find_element_by_link_text("37-117-20326-00-00").click()
        driver.find_element_by_xpath("//em[normalize-space(.)='FracEvent: -77.066594E 41.932717N @ Jan. 3, 2011, 6 p.m.']").click()
        driver.find_element_by_link_text("Shell").click()
        driver.find_element_by_link_text("Carrier/Base Fluid").click()
        self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text, r"^[\s\S]*ChemicalPurpose: Carrier/Base Fluid[\s\S]*$")
        self.assertTrue(self.is_element_present(By.CSS_SELECTOR, "body.appomatic_siteinfo-models-ChemicalPurpose"))

    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
