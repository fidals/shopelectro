"""
Create testing DB.

NOTE:
    1. It will purge all the existing data from DB.
    2. It creates random entities, so, tests likely will not pass with new data
    3. It overwrites shopelectro/fixtures/dump.json
    4. It can only run if your default database called `test`.
"""

from itertools import chain

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

from shopelectro.models import Product, Category
from pages.models import Page


class Command(BaseCommand):

    def handle(self, *args, **options):
        # We need to be sure that this command will run only on
        # 'test' DB.
        assert settings.DATABASES['default']['NAME'] == 'test'

        self._product_id = 0

        self.clear_tables()
        roots = self.create_root(2)
        children = self.create_children(2, roots)
        deep_children = self.create_children(2, children)
        self.create_products(list(deep_children))
        self.create_page()
        self.save_dump()

    @staticmethod
    def save_dump():
        """Save .json dump to fixtures."""
        call_command('dumpdata',
                     'shopelectro.Category',
                     'shopelectro.Product',
                     'pages.Page',
                     output='shopelectro/fixtures/dump.json')

    @staticmethod
    def create_root(count):
        get_name = 'Category #{}'.format
        return [Category.objects.create(name=get_name(i)) for i in range(count)]

    @property
    def product_id(self):
        self._product_id = self._product_id + 1
        return self._product_id

    @staticmethod
    def create_children(count, parents):
        name = 'Category #{} of #{}'

        def __create_categories(name, parent):
            return Category.objects.create(name=name, parent=parent)

        def __get_name(number, parent=None):
            return name.format(number, parent)

        return chain(*[
            [__create_categories(__get_name(i, parent), parent) for i in range(count)]
            for parent in parents
        ])

    def create_products(self, deep_children):
        """Create products for every non-root category."""
        def __create_product(categories, product_count):
            for category in categories:
                for i in range(1, product_count + 1):
                    Product.objects.create(
                        id=self.product_id,
                        name='Product #{} of {}'.format(i, category),
                        price=i * 100,
                        category=category,
                        wholesale_small=i * 75,
                        wholesale_medium=i * 50,
                        wholesale_large=i * 25,
                    )
        # Create 25 products for
        # tests_selenium.CategoryPage.test_load_more_hidden_in_fully_loaded_categories
        __create_product(deep_children[4:], 25)
        # Create 50 products for tests_selenium.CategoryPage.test_load_more_products
        __create_product(deep_children[:4], 50)

    @staticmethod
    def create_page():
        """Create only one page with type=FLAT_PAGE"""
        Page.objects.create(
            slug='flat',
            type=Page.FLAT_TYPE,
        )

    @staticmethod
    def clear_tables():
        """Remove everything from Category, Product and Page tables."""
        Category.objects.all().delete()
        Product.objects.all().delete()
        Page.objects.all().delete()
