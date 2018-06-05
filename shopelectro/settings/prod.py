from .base import *


DEBUG = False

ALLOWED_HOSTS = ['*']

if not os.environ.get('TEST_ENV', False):
    # http->https change
    os.environ['HTTPS'] = 'on'

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

YANDEX_KASSA_LINK = 'https://money.yandex.ru/eshop.xml'

USE_CELERY = True

REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']

REDIS_DSN = f'redis://{REDIS_URL}:{REDIS_PORT}/'

REDIS_LOCATION_DEFAULT = os.environ['REDIS_LOCATION_DEFAULT']
REDIS_LOCATION_SESSION = os.environ['REDIS_LOCATION_SESSION']
REDIS_LOCATION_THUMBNAIL = os.environ['REDIS_LOCATION_THUMBNAIL']
REDIS_LOCATION_USER_AGENT = os.environ['REDIS_LOCATION_USER_AGENT']


def redis_cache_template(options: dict=None) -> dict:
    options = options or {}
    return {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'{REDIS_DSN}{REDIS_LOCATION_DEFAULT}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': REDIS_PASSWORD,
            **options,
        }
    }


CACHES = {
    'default': redis_cache_template(
        {'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor'}
    ),
    'sessions': redis_cache_template(
        {'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',}
    ),
    'thumbnail': redis_cache_template(),
    'user_agents': redis_cache_template(),
}

THUMBNAIL_CACHE = 'thumbnail'
USER_AGENTS_CACHE = 'user_agents'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

SLACK_REPORT_URL = os.environ.get('SLACK_REPORT_URL', None)
