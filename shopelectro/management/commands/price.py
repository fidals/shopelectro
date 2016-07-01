"""
yml_price command.

Generate two price files: priceru.xml and yandex.yml.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from catalog.models import Category
from shopelectro.models import Product
from shopelectro import config


class Command(BaseCommand):
    """Generate yml file for a given vendor (YM or price.ru)."""

    def handle(self, *args, **options):
        """Parse target-argument and writes catalog to file."""
        targets = [('YM', 'yandex.yml'),
                   ('priceru', 'priceru.xml')]

        for utm, file_to_write in targets:
            self.write_yml(file_to_write, self.get_context_for_yml(utm))

    @staticmethod
    def get_context_for_yml(utm):
        """Create context dictionary for rendering files."""

        def put_utm(product):
            """Put UTM attribute to product."""
            def product_utm():
                return {
                    'utm_source': utm,
                    'utm_medium': 'cpc',
                    'utm_content': product.get_root_category().slug,
                    'utm_term': str(product.id)
                }
            url = reverse('product', args=(product.id,))
            utm_mark = '&'.join(['{}={}'.format(k, v)
                                 for k, v in product_utm().items()])
            product.utm_url = ''.join([settings.BASE_URL, url, utm_mark])
            return product

        others = (Category.objects.get(name='Прочее')
                  .get_descendants(include_self=True))
        categories_except_others = Category.objects.exclude(pk__in=others)
        products_except_others = (put_utm(product)
                                  for product in
                                  Product.objects.filter(
                                      category__in=categories_except_others)
                                  .filter(price__gt=0))
        return {
            'base_url': settings.BASE_URL,
            'categories': categories_except_others,
            'products': products_except_others,
            'shop': config.SHOP,
            'utm': utm,
        }

    @staticmethod
    def write_yml(file_to_write, context):
        """Write generated context to file."""
        with open(file_to_write, 'w', encoding='utf-8') as file:
            file.write(render_to_string('prices/price.yml', context).strip())
