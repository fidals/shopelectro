from django.conf import settings


def shop(request):
    """
    Injects shop dict into request.

    Shop dict contains information about shop:
    emails, phones, API-integrations.
    """
    return {
        'shop': settings.SHOP,
        'DEBUG': settings.DEBUG
    }
