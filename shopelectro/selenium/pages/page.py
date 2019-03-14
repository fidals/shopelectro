from functools import wraps

from shopelectro.selenium import SiteDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Page:
    """
    Represent a typical Shopelectro's page.

    Contains cross-page elements: header, footer, ...
    """

    def __init__(self, driver: SiteDriver):
        if not isinstance(driver, SiteDriver):
            raise TypeError('Driver must be an instance of shopelectro.selenium.SiteDriver')
        self.driver = driver
        self.path: str

    def wait_loaded(self):
        def loaded(driver):
            is_sync = EC.url_contains(self.path)
            is_rendered = EC.visibility_of_element_located(
                (By.TAG_NAME, 'body')
            )
            return is_sync(driver) and is_rendered(driver)
        self.driver.wait.until(loaded)

    def load(self):
        if not self.path:
            raise ValueError(f'Set a page path to {self.__class__.__name__}')
        self.driver.get(self.path)
        self.wait_loaded()
