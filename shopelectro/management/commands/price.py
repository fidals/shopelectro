import os
import typing
from collections import defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q, QuerySet
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


# --- data ---
class PriceFilter:
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

    def __init__(self, utm: str):
        assert utm in settings.UTM_PRICE_MAP
        self.utm = utm

    def run(self, query_set: QuerySet) -> QuerySet:
        return self.FILTERS[self.utm](query_set)


class Context(newcontext.Context):
    """DB data, extracted for price file."""

    UTM_MEDIUM_DATA = defaultdict(
        lambda: 'cpc',
        {'YM': 'cpc-market'}
    )

    IGNORED_CATEGORIES = [
        'Измерительные приборы', 'Новогодние вращающиеся светодиодные лампы',
        'Новогодние лазерные проекторы', 'MP3- колонки', 'Беспроводные звонки',
        'Радиоприёмники', 'Фонари', 'Отвертки', 'Весы электронные портативные',
    ]

    # dict keys are url targets for every service
    IGNORED_CATEGORIES_MAP = defaultdict(list, {
        'GM': ['Усилители звука для слабослышащих'],
    })

    def __init__(self, target: str):
        self.target = target

    # @todo #666:120m  Split price.Context.context to smaller classes
    #  Don't forget it:
    #  - Move class `PriceFilter` to `Product`
    #  - Merge to `IGNORED` constants
    #  - Rm constants from Tree class
    #  - Inject logs object here instead of returning operation status
    #  - Maybe split this file to blocks
    def context(self) -> dict:
        def put_utm(product):
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

        def put_crumbs(product):  # Ignore PyDocStyleBear
            """Crumbs for google merchant. https://goo.gl/b0UJQp"""
            product.crumbs = ' > '.join(
                product.page.get_ancestors_fields('h1', include_self=False)[1:]
            )
            return product

        def put_brand(product, brands):
            product.brand = brands.get(product)
            return product

        def filter_categories(utm):
            categories_to_exclude = (
                models.Category.objects
                .filter(
                    Q(name__in=self.IGNORED_CATEGORIES)
                    | Q(name__in=self.IGNORED_CATEGORIES_MAP[utm])
                )
                .get_descendants(include_self=True)
            )

            result_categories = models.Category.objects.exclude(id__in=categories_to_exclude)

            if utm == 'YM':
                """
                Yandex Market feed requires items in some categories to have pictures
                To simplify filtering we are excluding all categories
                which don't contain at least one product with picture
                """
                result_categories = result_categories.get_categories_tree_with_pictures()

            return result_categories

        def prepare_products(categories_, utm):
            """Filter product list and patch it for rendering."""
            products = PriceFilter(utm).run(
                models.Product.objects.active()
                .bind_fields()
                .filter(categories__in=categories_, price__gt=0)
            )
            brands = models.Tag.objects.get_brands(products)
            return [
                put_brand(put_crumbs(put_utm(product)), brands)
                for product in products
            ]

        categories = (
            filter_categories(self.target) if self.target != 'SE78'
            else models.Category.objects.all()
        )

        products = prepare_products(categories, self.target)

        return {
            'base_url': settings.BASE_URL,
            'categories': categories,
            'products': products,
            'shop': settings.SHOP,
            'utm': self.target,
        }


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
