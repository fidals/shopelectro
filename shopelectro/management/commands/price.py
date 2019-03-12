"""
Django command to generate yml price files for market-places.

`utm` or `target` defines particular market-place.
See `settings.UTM_PRICE_MAP` to explore current list of supported market-places.
"""

import logging
import os
import typing
from collections import defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import QuerySet
from django.template.loader import render_to_string

from catalog import newcontext
from shopelectro import models

logger = logging.getLogger(__name__)


# --- files processing ---
class File:
    def __init__(self, path: str, context: dict):
        self.path = path
        self.context = context

    def create(self):
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(render_to_string('prices/price.yml', self.context).strip())
        logger.info(f'{self.path} generated.')


class Files:
    def __init__(self, files: typing.List[File]):
        self.files = files

    def create(self):
        for file in self.files:
            file.create()


class Context(newcontext.Context):
    """DB data, extracted for price file."""

    def __init__(self, target: str):
        self.target = target

    def context(self) -> dict:
        categories = CategoriesFilter(self.target).qs()
        products = ProductsPatch(
            self.target,
            products=ProductsFilter(self.target, categories).qs()
        ).products()

        return {
            'base_url': settings.BASE_URL,
            'categories': categories,
            'products': products,
            'shop': settings.SHOP,
            'utm': self.target,
        }


class CategoriesFilter:
    """Categories list for particular market place."""

    # dict keys are url targets for every service
    IGNORED_CATEGORIES_MAP = defaultdict(list, {
        'GM': ['Усилители звука для слабослышащих'],
        # will be ignored by every category
        'default': [
            'Измерительные приборы', 'Новогодние вращающиеся светодиодные лампы',
            'Новогодние лазерные проекторы', 'MP3- колонки', 'Беспроводные звонки',
            'Радиоприёмники', 'Фонари', 'Отвертки', 'Весы электронные портативные',
            'Пиротехника',
        ]
    })

    @property
    def ignored(self) -> typing.List[str]:
        return (
            self.IGNORED_CATEGORIES_MAP['default']
            + self.IGNORED_CATEGORIES_MAP[self.target]
        )

    def __init__(self, target: str):
        assert target in settings.UTM_PRICE_MAP
        self.target = target

    def qs(self) -> models.SECategoryQuerySet:
        if self.target == 'SE78':
            return models.Category.objects.all()

        result_categories = (
            models.Category.objects
            .exclude(
                id__in=(
                    models.Category.objects
                    .filter(name__in=self.ignored)
                    .get_descendants(include_self=True)
                )
            )
        )

        if self.target == 'YM':
            """
            Yandex Market feed requires items in some categories to have pictures.
            To simplify filtering we are excluding all categories
            which don't contain at least one product with picture.
            """
            # @todo #715:30m  Try to rm ancestors filter in YM price filter.
            #  Exclude only categories with no pictures, without their ancestors.
            result_categories = result_categories.get_categories_tree_with_pictures()

        return result_categories


class ProductsFilter:
    """Filter offers with individual price requirements."""

    FILTERS = defaultdict(
        lambda: (lambda qs: qs),
        # Yandex Market feed requires picture for every offer
        YM=lambda qs: (
            qs
            .filter(page__images__isnull=False)
            .distinct()
        ),
        # Google Merchant feed should not contain offers cheaper then CONST
        GM=lambda qs: (
            qs
            .filter(price__gt=settings.PRICE_GM_LOWER_BOUND)
        )
    )

    def __init__(self, target: str, categories: models.SECategoryQuerySet):
        assert target in settings.UTM_PRICE_MAP
        self.target = target
        self.categories = categories

    def qs(self) -> QuerySet:
        return self.FILTERS[self.target](
            models.Product.objects.active()
            .filter(category__in=self.categories, price__gt=0)
        )


class ProductsPatch:

    UTM_MEDIUM_DATA = defaultdict(
        lambda: 'cpc',
        {'YM': 'cpc-market'}
    )

    def __init__(self, target: str, products: QuerySet):
        assert target in settings.UTM_PRICE_MAP
        self.target = target
        self._products = products

    def put_params(self, product):
        product.prepared_params = [
            (group, tags[0].name)
            for (group, tags) in filter(
                lambda x: x[0].name != 'Производитель',
                product.get_params().items()
            ) if tags
        ]
        return product

    def put_utm(self, product):
        """Put UTM attribute to product."""
        utm_marks = [
            ('utm_source', self.target),
            ('utm_medium', self.UTM_MEDIUM_DATA[self.target]),
            ('utm_content', product.get_root_category().page.slug),
            ('utm_term', str(product.vendor_code)),
        ]

        utm_mark_query = '&'.join(f'{k}={v}' for k, v in utm_marks)
        product.utm_url = f'{settings.BASE_URL}{product.url}?{utm_mark_query}'

        return product

    def put_crumbs(self, product):  # Ignore PyDocStyleBear
        """Crumbs for google merchant. https://goo.gl/b0UJQp"""
        product.crumbs = ' > '.join(
            product.page.get_ancestors_fields('h1', include_self=False)[1:]
        )
        return product

    def put_brand(self, product, brands):
        product.brand = brands.get(product)
        return product

    def products(self) -> typing.List[models.Product]:
        """Path every product with additional fields."""
        brands = models.Tag.objects.get_brands(self._products)
        return [
            self.put_brand(
                product=self.put_params(self.put_crumbs(self.put_utm(product))),
                brands=brands
            )
            for product in self._products
        ]


# --- command block ---
class Command(BaseCommand):
    """Generate yml file for a given vendor (YM or price.ru)."""

    # price files will be stored at this dir
    BASE_DIR = settings.ASSETS_DIR

    def handle(self, *args, **options):
        Files(
            [File(
                path=os.path.join(self.BASE_DIR, filename),
                context=Context(target).context()
            ) for target, filename in settings.UTM_PRICE_MAP.items()]
        ).create()
