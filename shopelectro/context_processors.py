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
        'BASE_URL': settings.BASE_URL
    }
