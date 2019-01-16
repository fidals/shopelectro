from shopelectro.selenium import SiteDriver


class Page:
    """
    Represent a typical Shopelectro's page.

    Contains cross-page elements: header, footer, ...
    """

    def __init__(self, driver: SiteDriver):
        if not isinstance(self.driver, SiteDriver):
            raise TypeError('Driver must be an instance of shopelectro.selenium.SiteDriver')
        self.driver = driver
        self.path: str

    def load(self):
        if not self.path:
            raise ValueError(f'Set a page path to {self.__class__.__name__}')
        self.driver.get(self.path)
        self.driver.wait.until(EC.visibility_of_element_located(
            (By.TAG_NAME, 'body')
        ))
