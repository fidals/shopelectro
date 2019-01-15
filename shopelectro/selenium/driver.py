from urllib.parse import urljoin

from django.conf import settings
from selenium.webdriver.support.ui import WebDriverWait
from seleniumrequests import Remote


class SiteDriver(Remote):
    """Provide convenient access to the site."""

    def __init__(self, *, site_url, **kwargs):
        super().__init__(**kwargs)
        kwargs.setdefault('command_executor', settings.SELENIUM_URL)
        kwargs.setdefault('desired_capabilities', DesiredCapabilities.CHROME)

        self.site_url = site_url
        self.wait = WebDriverWait(self, settings.SELENIUM_WAIT_SECONDS)

    def get(self, url):
        super().get(urljoin(self.site_url, url))
