from shopelectro.selenium.driver import SiteDriver

from selenium.webdriver.support import expected_conditions as EC


class Button:

    def __init__(self, driver: SiteDriver, locator):
        self.driver = driver
        self.locator = locator

    def click(self):
        self.driver.wait.until(EC.element_to_be_clickable(
            self.locator
        )).click()
