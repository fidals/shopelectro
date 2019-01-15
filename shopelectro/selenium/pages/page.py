from shopelectro.selenium import SiteDriver


class Page:
    """Represent a typical Shopelectro's page.

    Contains cross-page elements: header, footer, ...
    """

    def __init__(self, driver: SiteDriver):
        assert isinstance(self.driver, SiteDriver), "Driver must be an instance of shopelectro.selenium.SiteDriver"
        self.driver = driver
        self.address: str

    def move_to(self):
        assert self.address, f"Set a page address to {self.__class__.__name__}"
        self.driver.get(self.address)
        self.driver.wait.until(EC.visibility_of_element_located(
            (By.TAG_NAME, 'body')
        ))
