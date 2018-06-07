"""Settings especially for drone CI."""

from .base import *


DEBUG = True

# http://bit.ly/sorl-thumbnail-docs
THUMBNAIL_DEBUG = True

SITE_DOMAIN_NAME = 'stage.shopelectro.ru'

YANDEX_KASSA_LINK = 'https://demomoney.yandex.ru/eshop.xml'

USE_CELERY = False
