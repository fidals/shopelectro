from .base import *

DEBUG = True

DATABASE_URL = 'postgres://postgres:11@db/se_dev'
DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        default=DATABASE_URL
    )
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'info@shopelectro.ru'
EMAIL_HOST_PASSWORD = '21b34b446a'
DEFAULT_FROM_EMAIL = 'info@shopelectro.ru'
DEFAULT_TO_EMAIL = 'info@shopelectro.ru'
SHOP_EMAIL = 'info@shopelectro.ru'

SITE_DOMAIN_NAME = 'stage.shopelectro.ru'
