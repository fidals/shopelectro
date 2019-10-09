"""Settings especially for drone CI."""

from .base import *


DEBUG = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# http://bit.ly/sorl-thumbnail-docs
THUMBNAIL_DEBUG = True

SITE_DOMAIN_NAME = 'stage.shopelectro.ru'

YANDEX_KASSA_LINK = 'https://demomoney.yandex.ru/eshop.xml'

SELENIUM_URL = os.environ.get('SELENIUM_URL', 'http://selenium:4444/wd/hub')
SELENIUM_WAIT_SECONDS = int(os.environ['SELENIUM_WAIT_SECONDS'])
SELENIUM_TIMEOUT_SECONDS = int(os.environ['SELENIUM_TIMEOUT_SECONDS'])
SELENIUM_IMPLICIT_WAIT = int(os.environ['SELENIUM_IMPLICIT_WAIT'])
