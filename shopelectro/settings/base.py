"""
Django settings for shopelectro project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from datetime import datetime

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'so_secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# http://bit.ly/sorl-thumbnail-docs
THUMBNAIL_DEBUG = False

ALLOWED_HOSTS = ['*']

if os.environ.get('TEST_ENV', False):
    # disable https in CI
    # https://docs.djangoproject.com/en/1.9/ref/settings/#secure-proxy-ssl-header
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')

# Enable in frame loading for Ya.Metric
# https://docs.djangoproject.com/es/1.10/ref/clickjacking/
# https://yandex.ru/support/metrika/general/counter-webvisor.xml#download-page
X_FRAME_OPTIONS = 'ALLOW-FROM http://webvisor.com'

# Application definition
INSTALLED_APPS = [
    # https://docs.djangoproject.com/en/1.9/ref/contrib/admin/#django.contrib.admin.autodiscover
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_user_agents',
    'generic_admin',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'debug_toolbar',
    'mptt',
    'widget_tweaks',
    'sorl.thumbnail',
    'django_select2',
    'images',
    'pages',
    'catalog',
    'search',
    'ecommerce',
    'shopelectro',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'shopelectro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ecommerce.context_processors.cart',
                'shopelectro.context_processors.shop',
            ],
        },
    },
]

WSGI_APPLICATION = 'shopelectro.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LOCALE_NAME = 'en_US'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, 'shopelectro/locale')]
FORMAT_MODULE_PATH = [
    'shopelectro.formats',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'front/build'),
    ASSETS_DIR,
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# @todo #142 Drop `dj_database_url` dependency.
#  This package helps to take postgres credentials from URI.
#  Now we assemble this creds to URI, then parse them with dj_database_url.
DATABASE_URL = (
    f'postgres://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}'
    f'@{os.environ["POSTGRES_URL"]}/{os.environ["POSTGRES_DB"]}'
)
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'pages': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'catalog': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'search': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'ecommerce': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'images': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'shopelectro': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

SELENIUM_URL = os.environ.get('SELENIUM_URL', 'http://selenium:4444/wd/hub')

SITE_CREATED = datetime(2013, 1, 1)

LOCALHOST = 'http://127.0.0.1:8000/'
BASE_URL = 'https://www.shopelectro.ru'

PLACEHOLDER_IMAGE = 'images/logo.png'
PLACEHOLDER_ALT = 'Логотип компании Shopelectro'

# Autocomplete and search settings
SEARCH_SEE_ALL_LABEL = 'Смотреть все результаты'

# For sitemaps and sites framework
SITE_ID = 1
SITE_DOMAIN_NAME = 'www.shopelectro.ru'

# Used to retrieve instances in ecommerce.Cart
CART_ID = 'cart'

# Used to define choices attr in definition of Order.payment_type field
PAYMENT_OPTIONS = (
    ('cash', 'Наличные'),
    ('cashless', 'Безналичные и денежные переводы'),
    ('AC', 'Банковская карта'),
    ('PC', 'Яндекс.Деньги'),
    ('GP', 'Связной (терминал)'),
    ('AB', 'Альфа-Клик'),
)

# It is fake-pass. Correct pass will be created on `docker-compose up` stage from `docker/.env`
YANDEX_SHOP_PASS = os.environ.get('YANDEX_SHOP_PASS', 'so_secret_pass')

# Used for order's email in ecommerce app
FAKE_ORDER_NUMBER = 6000

# Subjects for different types of emails sent from SE.
EMAIL_SUBJECTS = {
    'call': 'Обратный звонок',
    'order': 'Заказ №{0.fake_order_number}',
    'yandex_order': 'Заказ №{0.fake_order_number} | Яндекс.Касса',
    'one_click': 'Заказ в один клик №{0.fake_order_number}',
    'ya_feedback_request': 'Оцените нас на Яндекс.Маркете',
}

# Email configs
# It is fake-pass. Correct pass will be created on `docker-compose up` stage from `docker/.env`
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'so_secret_pass')
EMAIL_HOST_USER = 'info@shopelectro.ru'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_SENDER = 'info@shopelectro.ru'
EMAIL_RECIPIENT = 'info@shopelectro.ru'
SHOP_EMAIL = 'info@shopelectro.ru'

# FTP configs
FTP_USER = os.environ.get('FTP_USER', 'user')
FTP_PASS = os.environ.get('FTP_PASS', 'pass')
FTP_IP = os.environ.get('FTP_IP', '0.0.0.0')

ENV_TYPE = os.environ.get('ENV_TYPE', 'PROD')  # LOCAL | CI | PROD

# 'Prod' <-> 'Product #1 of Category #0 of Category #1' = 0.17
# About trigram similarity: https://goo.gl/uYFcxN
TRIGRAM_MIN_SIMILARITY = 0.15

# Used in admin image uploads
MODEL_TYPES = {
    'Product': {
        'app_name': 'shopelectro',
        'dir_name': 'products',
    },
    'Category': {
        'app_name': 'shopelectro',
        'dir_name': 'categories',
    }
}

# This need for using {% debug %} variable in templates.
INTERNAL_IPS = (
    '127.0.0.1',
)

TOP_PRODUCTS = [291, 438, 1137, 2166, 2725, 2838, 3288, 3884, 3959, 2764]
CATEGORY_STEP_MULTIPLIERS = [12, 15, 24, 25, 48, 50, 60, 100]

# Reduce retail product prices by PRICE_REDUCER.
# It is required to make prices on shopelectro.ru and se78.ru unique.
PRICE_REDUCER = 1

SHOP = {
    'id': '69886',
    'scid': '64788',
    'success_url': BASE_URL + '/shop/order-success/',
    'fail_url': BASE_URL + '/',
    'cps_phone': '+78124163200',
    'cps_email': 'info@shopelectro.ru',
    'local_delivery_cost': 300,
    'local_delivery_cost_threshold': 5000,
}

# used in data-migrations and tests
CUSTOM_PAGES = {
    'index': {
        'slug': '',
        'name': 'Интернет-магазин элементов питания "ShopElectro"',
        'menu_title': 'Главная',
        'title': 'Интернет-магазин Элементов питания с доставкой по России',
    },
    'sitemap': {
        'slug': 'sitemap',
        'h1': 'Карта сайта',
        'name': 'Карта сайта',
    },
    'order': {
        'slug': 'order',
        'name': 'Оформление заказа',
        'title': 'Корзина Интернет-магазин shopelectro.ru Санкт-Петербург',
    },
    'search': {
        'slug': 'search',
        'name': 'Результаты поиска',
    },
    'catalog': {
        'slug': 'catalog',
        'name': 'Каталог товаров',
        'menu_title': 'Каталог',
    },
    'order_success': {
        'slug': 'order-success',
        'name': 'Заказ принят',
    }
}

TAGS_URL_DELIMITER = '-or-'
TAG_GROUPS_URL_DELIMITER = '-and-'

TAGS_TITLE_DELIMITER = ' или '
TAG_GROUPS_TITLE_DELIMITER = ' и '

TAGS_ORDER = ['group__position', 'group__name', 'position', 'name']

# -- App business logic --
# every product price will be multiplied on this value
# during import from 1C.
# Multipliers are related to prices in this order:
# big/medium/small/retail. First three are wholesale prices.
PRICE_MULTIPLIERS = 1.0, 1.0, 1.0, 1.0
