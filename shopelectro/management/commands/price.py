"""
yml_price command.

Generate price files.
"""

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.db import close_old_connections
from django.template.loader import render_to_string

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

    def create_prices(self, parallel=None):
        if not parallel:
            for x,y in self.TARGETS.items():
                self.generate_yml(x, y)
        else:
            with ProcessPoolExecutor(parallel or cpu_count()) as executor:
                futures = [
                    executor.submit(self.generate_yml, *target)
                    for target in self.TARGETS.items()
                ]

                for future in as_completed(futures):
                    print(future.result())

    def add_arguments(self, parser):
        parser.add_argument(
            '--parallel',
            nargs='*',
            default=None,
            type=int,
        )

    def handle(self, *args, **options):
        if options['parallel']:
            close_old_connections()  # Set transaction isolation level
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
                ('utm_term', str(product.id)),
            ]
            url = reverse('product', args=(product.id,))
            utm_mark_query = '&'.join('{}={}'.format(k, v) for k, v in utm_marks)
            product.utm_url = '{}{}?{}'.format(settings.BASE_URL, url, utm_mark_query)

            return product

        def put_crumbs(product):
            """
            Crumbs for google merchant. https://goo.gl/b0UJQp
            """
            product.crumbs = ' > '.join(
                product.page.get_ancestors_fields('h1', include_self=False)[1:]
            )
            return product

        def filter_categories():
            categories_to_exclude = (
                Category.objects
                    .filter(name__in=cls.IGNORED_CATEGORIES)
                    .get_descendants(include_self=True)
            )

            return Category.objects.exclude(id__in=categories_to_exclude)

        def prepare_products(categories_):
            """Filter product list and patch it for rendering"""
            products_except_others = (
                Product.objects
                    .select_related('page')
                    .prefetch_related('category')
                    .filter(category__in=categories_, price__gt=0)
            )

            result_products = [
                put_crumbs(put_utm(product))
                for product in products_except_others.iterator()
            ]

            return result_products

        categories = (
            filter_categories() if utm != 'SE78'
            else Category.objects.all()
        )

        return {
            'base_url': settings.BASE_URL,
            'categories': categories,
            'products': prepare_products(categories),
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
