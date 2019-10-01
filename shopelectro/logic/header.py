import typing
from functools import lru_cache

from django.conf import settings
from django.db.models import Q

from pages import models as pages_models
from shopelectro import models


class Menu:
    DICT_TYPE = typing.Dict[models.CategoryPage, typing.List[models.CategoryPage]]

    @staticmethod
    def roots() -> pages_models.PageQuerySet:
        """
        QuerySet with header menu items.

        Contains root categories.
        Result can be tuned HEADER_LINKS settings option.
        """
        return (
            pages_models.Page.objects.active()
            .filter(
                Q(slug__in=settings.HEADER_LINKS['add'])
                | (
                    # @todo #974:30m  Optimize the header menu query.
                    #  Fetch catalog page for the header menu at the same query.
                    #  root category pages.
                    Q(parent=pages_models.CustomPage.objects.filter(slug='catalog'))
                    & Q(type='model')
                    & Q(related_model_name=models.Category._meta.db_table)
                    & ~Q(slug__in=settings.HEADER_LINKS['exclude'])
                )
            )
            .order_by('position')
        )

    @lru_cache(maxsize=1)
    def as_dict(self) -> DICT_TYPE:
        return {
            root: list(
                root.get_children()
                .filter(type='model')
                .filter(related_model_name=models.Category._meta.db_table)
            )
            for root in self.roots().iterator()
        }
