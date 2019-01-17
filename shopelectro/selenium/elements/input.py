import re

from shopelectro.selenium.conditions import TextPresentedInValue
from shopelectro.selenium.driver import SiteDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Input:

    def __init__(self, driver: SiteDriver, locator):
        self.driver = driver
        self.locator = locator

    def send_keys(self, keys: str):
        keys = str(keys)
        if not re.match(r'[\w\d\s\-_]+', keys, re.I | re.U):
            raise ValueError('Form text should not contain special symbols')
        el = self.driver.wait.until(EC.element_to_be_clickable(self.locator))
        el.clear()
        el.send_keys(keys)
        self.driver.wait.until(TextPresentedInValue(self.locator, keys))
