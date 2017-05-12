from .base import *


DEBUG = False

ALLOWED_HOSTS = ['*']

# enable https if we're not in continuous integration
if not os.environ.get('CONTINUOUS_INTEGRATION', None):
    # http->https change

    os.environ['HTTPS'] = 'on'

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
else:
    SECURE_PROXY_SSL_HEADER = None

YANDEX_KASSA_LINK = 'https://money.yandex.ru/eshop.xml'

USE_CELERY = True

REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_LOCATION_DEFAULT', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'PASSWORD': REDIS_PASSWORD,
        }
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_LOCATION_SESSION', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'PASSWORD': REDIS_PASSWORD,
        }
    },
    'thumbnail': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_LOCATION_THUMBNAIL', 'redis://127.0.0.1:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': REDIS_PASSWORD,
        }
    },
    'user_agents': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_LOCATION_USER_AGENT', 'redis://127.0.0.1:6379/3'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': REDIS_PASSWORD,
        }
    },
}

THUMBNAIL_CACHE = 'thumbnail'
USER_AGENTS_CACHE = 'user_agents'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

SLACK_REPORT_URL = os.environ.get('SLACK_REPORT_URL', None)
