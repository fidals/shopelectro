from collections import defaultdict
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q, QuerySet
from django.template.loader import render_to_string
from django.urls import reverse

from shopelectro.models import Product, Category, Tag


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


class Command(BaseCommand):
    """Generate yml file for a given vendor (YM or price.ru)."""

    # price files will be stored at this dir
    BASE_DIR = settings.ASSETS_DIR

    IGNORED_CATEGORIES = [
        'Измерительные приборы', 'Новогодние вращающиеся светодиодные лампы',
        'Новогодние лазерные проекторы', 'MP3- колонки', 'Беспроводные звонки',
        'Радиоприёмники', 'Фонари', 'Отвертки', 'Весы электронные портативные',
    ]

    IGNORED_CATEGORIES_BY_TARGET = defaultdict(list, {
        'GM': ['Усилители звука для слабослышащих'],
    })

    def create_prices(self):
        for target in settings.UTM_PRICE_MAP.items():
            self.generate_yml(*target)

    def handle(self, *args, **options):
        self.create_prices()

    @classmethod
    def get_context_for_yml(cls, utm):
        """Create context dictionary for rendering files."""
        def put_utm(product):
            """Put UTM attribute to product."""
            utm_marks = [
                ('utm_source', utm),
                ('utm_medium', 'cpc'),
                ('utm_content', product.get_root_category().page.slug),
                ('utm_term', str(product.vendor_code)),
            ]

            url = reverse('product', args=(product.vendor_code,))
            utm_mark_query = '&'.join('{}={}'.format(k, v) for k, v in utm_marks)
            product.utm_url = '{}{}?{}'.format(settings.BASE_URL, url, utm_mark_query)

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
                Category.objects
                .filter(
                    Q(name__in=cls.IGNORED_CATEGORIES)
                    | Q(name__in=cls.IGNORED_CATEGORIES_BY_TARGET[utm])
                )
                .get_descendants(include_self=True)
            )

            result_categories = Category.objects.exclude(id__in=categories_to_exclude)

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
                Product.objects.active().filter_by_categories(categories_)
            )
            brands = Tag.objects.get_brands(products)
            return [
                put_brand(put_crumbs(put_utm(product)), brands)
                for product in products
            ]

        categories = (
            filter_categories(utm) if utm != 'SE78'
            else Category.objects.all()
        )

        products = prepare_products(categories, utm)

        return {
            'base_url': settings.BASE_URL,
            'categories': categories,
            'products': products,
            'shop': settings.SHOP,
            'utm': utm,
        }

    @classmethod
    def generate_yml(cls, utm, file_name):
        """Generate yml file."""
        file_to_write = os.path.join(cls.BASE_DIR, file_name)
        context = cls.get_context_for_yml(utm)

        with open(file_to_write, 'w', encoding='utf-8') as file:
            file.write(render_to_string('prices/price.yml', context).strip())

        return '{} generated...'.format(file_name)
