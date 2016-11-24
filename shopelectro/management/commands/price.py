"""
yml_price command.

Generate two price files: priceru.xml and yandex.yml.
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
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
    }
    # price files will be stored at this dir
    BASE_DIR = settings.ASSETS_DIR

    def create_prices(self):
        for utm, file_name in self.TARGETS.items():
            result_file = os.path.join(self.BASE_DIR, file_name)
            self.write_yml(result_file, self.get_context_for_yml(utm))

    def handle(self, *args, **options):
        self.create_prices()

    @staticmethod
    def get_context_for_yml(utm):
        """Create context dictionary for rendering files."""

        def put_utm(product):
            """Put UTM attribute to product."""
            utm_marks = {
                'utm_source': utm,
                'utm_medium': 'cpc',
                'utm_content': product.get_root_category().page.slug,
                'utm_term': str(product.id)
            }
            url = reverse('product', args=(product.id,))
            utm_mark = '&'.join(
                ['{}={}'.format(k, v) for k, v in utm_marks.items()]
            )
            product.utm_url = ''.join([settings.BASE_URL, url, '?' + utm_mark])

            return product

        def put_crumbs(product):
            """
            Crumbs for google merchant.
            Google merchant doc: https://goo.gl/b0UJQp
            """
            product.crumbs = ' > '.join(
                product.page.get_ancestors_fields('h1', include_self=False)[1:]
            )
            return product

        def filter_categories():
            new_year_lights = Category.objects.get(name='Новогодние гирлянды').get_descendants(include_self=True)
            others = (
                Category.objects.get(name='Прочее')
                                .get_descendants(include_self=True)
                                .exclude(pk__in=new_year_lights)
            )

            return Category.objects.exclude(pk__in=others)

        def prepare_products(categories):
            """Filter product list and patch it for rendering"""
            products_except_others = Product.objects.filter(
                category__in=categories).filter(price__gt=0)
            result_products = (
                put_crumbs(put_utm(product))
                for product in products_except_others
            )

            return result_products

        filtered_categories = filter_categories()

        return {
            'base_url': settings.BASE_URL,
            'categories': filtered_categories,
            'products': prepare_products(filtered_categories),
            'shop': settings.SHOP,
            'utm': utm,
        }

    @staticmethod
    def write_yml(file_to_write, context):
        """Write generated context to file."""
        with open(file_to_write, 'w', encoding='utf-8') as file:
            file.write(render_to_string('prices/price.yml', context).strip())
