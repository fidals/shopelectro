"""
Django settings for shopelectro project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os
import socket
from datetime import datetime

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
    'django_extensions',
    'generic_admin',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'debug_toolbar',
    'mptt',
    'widget_tweaks',
    'sorl.thumbnail',
    'django_select2',
    'images',
    'refarm_redirects',
    'pages',
    'catalog',
    'search',
    'ecommerce',
    'refarm_test_utils',
    'shopelectro',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'refarm_redirects.middleware.RedirectAllMiddleware',
]

ROOT_URLCONF = 'shopelectro.urls'

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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
    os.path.join(BASE_DIR, 'front_build'),
    ASSETS_DIR,
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DATABASE_URL = os.environ["POSTGRES_URL"]

# to activate django connections pool for persistent connections.
# https://docs.djangoproject.com/en/1.11/ref/databases/#persistent-connections
CONN_MAX_AGE = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_URL'],
        'PORT': '5432',
    }
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

TEST_RUNNER = 'refarm_test_utils.runners.RefarmTestRunner'
# address for selenium-based tests
# CI doesn't resolve a host name, so we have to use the host address
LIVESERVER_HOST = socket.gethostbyname(socket.gethostname())

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
EMAIL_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS', 'info@shopelectro.ru').split(',')

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
    'cps_formatted_phone': '416-32-00',
    'cps_email': 'info@shopelectro.ru',
    'local_delivery_cost': 300,
    'local_delivery_cost_threshold': 5000,
}


def get_robots_content():
    with open(os.path.join(TEMPLATE_DIR, 'robots.txt')) as robots_file:
        return robots_file.read()

# @todo #265:60m Move content-based settings to db.
#  Content guys should be able to change settings like
#  `MAIN_PAGE_TILE` or `FOOTER_LINKS` from admin panel.


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
    },
    'robots': {
        'slug': 'robots.txt',
        'content': get_robots_content(),
    },
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

# default for local tests. Prod's one may differ
YANDEX_KASSA_LINK = 'https://money.yandex.ru/eshop.xml'

PRODUCT_SIBLINGS_COUNT = 10

CATEGORY_SORTING_OPTIONS ={
    0: {
        'label': 'Цене, сначала дешёвые',
        'field': 'price',
        'direction': ''
    },
    1: {
        'label': 'Цене, сначала дорогие',
        'field': 'price',
        'direction': '-'
    },
    2: {
        'label': 'Названию, А-Я',
        'field': 'name',
        'direction': ''
    },
    3: {
        'label': 'Названию, Я-А',
        'field': 'name',
        'direction': '-'
    },
    4: {
        'label': 'Артикулу',
        'field': 'vendor_code',
        'direction': ''
    },
}

# Tile on main page.
# Every link should have either slug or url.
MAIN_PAGE_TILE = {
    'accumulators': [
        {'name': 'Типоразмера AA',
         'url': '/catalog/categories/akkumuliatory-270/tags/aa/'},
        {'name': 'Типоразмера ААА',
         'url': '/catalog/categories/akkumuliatory-270/tags/aaa/'},
        {'name': 'Для радиомоделей и игрушек',
         'slug': 'akkumuliatory-dlia-radioupravliaemykh-modelei-i-igrushek'},
        {'name': 'Свинцово-кислотные',
         'slug': 'akkumuliatory-svintsovo-kislotnye-4-v-6-v-12-v-lca'},
        {'name': 'Внешние универсальные',
         'slug': 'vneshnie-universalnye-akkumuliatory'},
        {'name': 'Адаптеры, отсеки и футляры',
         'slug': 'adaptery-otseki-i-futliary-dlia-akkumuliatorov'},
    ],
    'inverter': [
        {'name': 'Инверторы', 'slug': 'invertory'},
        {'name': 'Преобразователи DC 24 В/12 В KALLER',
         'slug': 'preobrazovateli-napriazheniia-dc-24-v12-v-kaller'},
    ],
    'batteries': [
        {'name': 'Типоразмера АА', 'slug': 'batareiki-aa'},
        {'name': 'Часовые', 'slug': 'chasovye-batareiki-alkalinovye'},
        {'name': 'Дисковые литиевые', 'slug': 'diskovye-litievye-batareiki-3-v'},
    ],
    'lights': [
        {'name': 'Ручные', 'url': '/catalog/categories/fonari-226/tags/ruchnoi/'},
        {'name': 'Налобные', 'url': '/catalog/categories/fonari-226/tags/nalobnyi/'},
        {'name': 'Туристические', 'url': '/categories/fonari-226/tags/kempingovye/'},
        {'name': 'Автомобильные', 'slug': 'avtomobilnye-fonari'},
    ],
    'chargers': [
        {'name': 'Для фотоаппаратов',
         'slug': 'zariadnye-ustroistva-dlia-fotoapparatov'},
        {'name': 'Для видеокамер', 'slug': 'zariadnye-ustroistva-dlia-videokamer'},
        {'name': 'Для свинцовых',
         'slug': 'zariadnye-ustroistva-dlia-svintsovykh-akkumuliatorov'},
    ],
    'multimeters': [
        {'name': 'MY68 Master Professional', 'slug': '1411'},
        {'name': 'MY67 Master Professional', 'slug': '1692'},
        {'name': 'MY64 Master Professional', 'slug': '1407'},
    ],
    'adapters': [
        {'id': 1, 'name': '220В для ноутбуков',
         'slug': 'bloki-pitaniia-dlia-noutbukov-ot-seti-220v'},
        {'id': 1, 'name': '12В для ноутбуков',
         'slug': 'bloki-pitaniia-dlia-noutbukov-ot-seti-12v'},
        {'id': 1, 'name': 'Трансформаторные',
         'slug': 'bloki-pitaniia-transformatornye'},
    ],
}

FOOTER_LINKS = {
    'services': [
        {'name': 'Ремонт аккумуляторов', 'slug': 'remont-akkumulyatorov'},
        {'name': 'Пайка на заказ', 'slug': 'soldering'},
        {'name': 'Доставка по всей России', 'slug': 'delivery'},
    ],
    'about': [
        {'name': 'Реквизиты', 'type': 'navigation', 'slug': 'rekvisity'},
        {'name': 'Купить оптом', 'type': 'articles', 'slug': 'wholesale'},
        {'name': 'Гарантии и возврат', 'type': 'navigation', 'slug': 'return-goods-instr'},
    ],
}

PRICE_BOUNDS = {
    'wholesale_large': 100000,
    'wholesale_medium': 50000,
    'wholesale_small': 20000,
}

BRAND_TAG_GROUP_NAME = 'Производитель'

# products with price lower this value should not be presented at gm.yml price
PRICE_GM_LOWER_BOUND = 200.0

# Online market services, that works with our prices.
# Dict keys - url targets for every service.
# @todo #666:30m  Move UTM_PRICE_MAP to an iterable Enum
UTM_PRICE_MAP = {
    'YM': 'yandex.yml',
    'priceru': 'priceru.xml',
    'GM': 'gm.yml',
    'SE78': 'se78.yml',
}

# Number of pagination neighbors shown for page.
# If PAGINATION_NEIGHBORS = 4 and number of a page = 5,
# then will be shown neighbors by number: 3, 4, 6, 7
PAGINATION_NEIGHBORS = 10

PRODUCTS_ON_PAGE_PC = 48
PRODUCTS_ON_PAGE_MOB = 12

TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
TG_REPORT_ADDRESSEES = os.environ.get(
    'TG_REPORT_ADDRESSEES', '@shopelectro_reports'
).split(',')
CHECK_PURCHASE_RETRIES = int(os.environ.get('CHECK_PURCHASE_RETRIES', '3'))
