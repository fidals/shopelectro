from .base import *


DEBUG = False

# http://bit.ly/sorl-thumbnail-docs
THUMBNAIL_DEBUG = False

ALLOWED_HOSTS = ['*']

# http->https change
os.environ['HTTPS'] = 'on'

YANDEX_KASSA_LINK = 'https://money.yandex.ru/eshop.xml'
