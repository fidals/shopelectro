from .base import *


DEBUG = True

# http://bit.ly/sorl-thumbnail-docs
THUMBNAIL_DEBUG = True

SITE_DOMAIN_NAME = 'stage.shopelectro.ru'

YANDEX_KASSA_LINK = 'https://demomoney.yandex.ru/eshop.xml'

USE_CELERY = False


def show_debug_toolbar(request):
    '''
    Show debug toolbar even if settings doesn't have INTERNAL_IPS list
    '''
    return True


DEBUG_TOOLBAR_PATCH_SETTINGS = False

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'shopelectro.settings.dev.show_debug_toolbar'
}
