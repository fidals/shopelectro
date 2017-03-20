from django.test import override_settings


set_default_staticfiles_storage = override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
)

disable_celery = override_settings(USE_CELERY=False)
