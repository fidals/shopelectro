from django.conf import settings


def shop(request):
    """
    Inject shop dict into request.

    Shop dict contains information about shop:
    emails, phones, API-integrations.
    """
    return {
        'shop': settings.SHOP,
        'DEBUG': settings.DEBUG,
        'base_url': settings.BASE_URL,
        'SENTRY_FRONT_DSN': settings.SENTRY_FRONT_DSN,
    }
