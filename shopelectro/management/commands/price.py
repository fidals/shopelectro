"""
Django command to generate yml price files for market-places.

`utm` or `target` defines particular market-place.
See `settings.UTM_PRICE_MAP` to explore current list of supported market-places.
"""

import os
import typing
from collections import defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.urls import reverse

from catalog import newcontext
from shopelectro import models


# --- files processing ---
class File:
    def __init__(self, path: str, context: dict):
        self.path = path
        self.context = context

    def create(self):
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(render_to_string('prices/price.yml', self.context).strip())
        return f'{self.path} generated...'


class Files:
    def __init__(self, files: typing.List[File]):
        self.files = files

    def create(self):
        for file in self.files:
            file.create()


class Price:
    pass


class Prices:
    pass


class Context(newcontext.Context):
    """DB data, extracted for price file."""

    def __init__(self, target: str):
        self.target = target

    # @todo #666:120m  Split price.Context.context to smaller classes
    #  Don't forget it:
    #  - Move class `PriceFilter` to `Product`
    #  - Rm constants from Tree class
    #  - Inject logs object here instead of returning operation status
    #  - Maybe split this file to blocks
    def context(self) -> dict:
        categories = Categories(self.target).filter()
        products = Products(self.target, parents=categories)

        return {
            'base_url': settings.BASE_URL,
            'categories': categories,
            'products': products.prepare(),
            'shop': settings.SHOP,
            'utm': self.target,
        }


class Categories:
    """Categories list for particular market place."""

    # dict keys are url targets for every service
    IGNORED_CATEGORIES_MAP = defaultdict(list, {
        'GM': ['Усилители звука для слабослышащих'],
        # will be ignored by every category
        'default': [
            'Измерительные приборы', 'Новогодние вращающиеся светодиодные лампы',
            'Новогодние лазерные проекторы', 'MP3- колонки', 'Беспроводные звонки',
            'Радиоприёмники', 'Фонари', 'Отвертки', 'Весы электронные портативные',
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

    # TODO - move to filter like Products.FILTERS
    def filter(self) -> models.SECategoryQuerySet:
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


class Products:
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

    UTM_MEDIUM_DATA = defaultdict(
        lambda: 'cpc',
        {'YM': 'cpc-market'}
    )

    def __init__(self, target: str, parents: models.SECategoryQuerySet):
        assert target in settings.UTM_PRICE_MAP
        self.target = target
        self.parents = parents

    def filter(self) -> QuerySet:
        return self.FILTERS[self.target](
            models.Product.objects.active().filter_by_categories(self.parents)
        )

    def put_utm(self, product):
        """Put UTM attribute to product."""
        utm_marks = [
            ('utm_source', self.target),
            ('utm_medium', self.UTM_MEDIUM_DATA[self.target]),
            ('utm_content', product.get_root_category().page.slug),
            ('utm_term', str(product.vendor_code)),
        ]

        url = reverse('product', args=(product.vendor_code,))
        utm_mark_query = '&'.join(f'{k}={v}' for k, v in utm_marks)
        product.utm_url = f'{settings.BASE_URL}{url}?{utm_mark_query}'

        product.prepared_params = [
            (group, tags[0].name)
            for (group, tags) in filter(
                lambda x: x[0].name != 'Производитель',
                product.get_params()
            ) if tags
        ]

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

    def prepare(self) -> typing.List[models.Product]:
        """Path every product with additional fields."""
        products = self.filter()
        brands = models.Tag.objects.get_brands(products)
        return [
            self.put_brand(self.put_crumbs(self.put_utm(product)), brands)
            for product in products
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
