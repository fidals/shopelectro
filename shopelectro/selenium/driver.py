from urllib.parse import urljoin

from seleniumrequests import Remote


class SiteDriver(Remote):
    """Provide convenient access to the site."""

    def __init__(self, *args, site_url='', **kwargs):
        self.site_url = site_url
        super().__init__(*args, **kwargs)

    def get(self, url):
        super().get(urljoin(self.site_url, url))
