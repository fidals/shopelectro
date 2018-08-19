from collections import defaultdict
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse

from shopelectro.models import Product, Category


class Command(BaseCommand):
    """Generate yml file for a given vendor (YM or price.ru)."""

    # Online market services, that works with our prices.
    # Dict keys - url targets for every service
    TARGETS = {
        'YM': 'yandex.yml',
        'priceru': 'priceru.xml',
        'GM': 'gm.yml',
        'SE78': 'se78.yml',
    }
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
        for target in self.TARGETS.items():
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

            product.prepared_params = list(
                filter(
                    lambda x: x[0].name != 'Производитель',
                    product.get_params()
                )
            )

            return product

        def put_crumbs(product):  # Ignore PyDocStyleBear
            """Crumbs for google merchant. https://goo.gl/b0UJQp"""
            product.crumbs = ' > '.join(
                product.page.get_ancestors_fields('h1', include_self=False)[1:]
            )
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
            products_except_others = (
                Product.actives
                .select_related('page')
                .prefetch_related('category')
                .prefetch_related('page__images')
                .filter(category__in=categories_, price__gt=0)
            )

            if utm == 'YM':
                """
                Yandex Market feed requires items in some categories to have pictures
                To simplify filtering we are excluding all products without pictures
                """
                products_except_others = (
                    products_except_others
                    .filter(page__images__isnull=False)
                    .distinct()
                )

            result_products = [
                put_crumbs(put_utm(product))
                for product in products_except_others
            ]

            return result_products

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
