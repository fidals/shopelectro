from .base import *

DEBUG = True

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'mediaprime10@yandex.ru'
EMAIL_HOST_PASSWORD = 'planka67rezka'
DEFAULT_FROM_EMAIL = 'mediaprime10@yandex.ru'
DEFAULT_TO_EMAIL = 'mediaprime10@yandex.ru'
SHOP_EMAIL = 'mediaprime10@yandex.ru'

DATABASE_URL = 'postgres://postgres:11@db/se_dev'

DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        default=DATABASE_URL
    )
}

SITE_DOMAIN_NAME = 'stage.shopelectro.ru'

#http->https change
# os.environ['HTTPS'] = 'on'
