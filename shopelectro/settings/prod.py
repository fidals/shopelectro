from .base import *


DEBUG = False

ALLOWED_HOSTS = ['*']

# http->https change
os.environ['HTTPS'] = 'on'

YANDEX_KASSA_LINK = 'https://money.yandex.ru/eshop.xml'

# Memcached settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_LOCATION', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
