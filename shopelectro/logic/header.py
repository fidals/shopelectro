from django.conf import settings
from django.db.models import Q

from pages import models as pages_models
from shopelectro import models


def menu_qs() -> pages_models.PageQuerySet:
    return (
        pages_models.Page.objects.active()
        .filter(
            Q(slug__in=settings.HEADER_LINKS['add'])
            & ~Q(slug__in=settings.HEADER_LINKS['exclude'])
            | (
                # @todo #974:30m  Optimize the header menu query.
                #  Fetch catalog page for the header menu at the same query.
                #  root category pages.
                Q(parent=pages_models.CustomPage.objects.filter(slug='catalog'))
                & Q(related_model_name=models.Category._meta.db_table)
                & Q(parent=pages_models.CustomPage.objects.filter(slug='catalog'))
            )
        )
        .order_by('position')
    )
