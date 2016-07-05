"""
Create testing DB.

NOTE:
    1. It will purge all the existing data from DB.
    2. It creates random entities, so, tests likely will not pass with new data
    3. It overwrites shopelectro/fixtures/dump.json
    4. It can only run if your default database called `test`.
"""


from random import randint

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

from catalog.models import Category

from shopelectro.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        # We need to be sure that this command will run only on
        # 'test' DB.
        assert settings.DATABASES['default']['NAME'] == 'test'

        self.clear_tables()
        roots = self.create_roots()
        for r in roots:
            self.create_children(r)
        self.create_deep_children()
        self.create_products()
        self.save_dump()

    def save_dump(self):
        """Save .json dump to fixtures."""
        call_command('dumpdata',
                     'shopelectro.Product',
                     'catalog.Product',
                     'catalog.Category',
                     output='shopelectro/fixtures/dump.json')

    def create_roots(self):
        """Create 2 root categories."""
        roots = []
        for i in range(2):
            r, _ = Category.objects.get_or_create(name='Root category #{}'.format(i))
            roots.append(r)
        return roots

    def create_children(self, category):
        """Create 3 children of a given category."""
        for i in range(3):
            Category.objects.create(name='Child #{} of #{}'.format(i, category),
                                    position=i,
                                    parent=category)

    def create_deep_children(self):
        """Create children of a last added non-root category."""
        last_child = Category.objects.last()
        self.create_children(last_child)

    def create_products(self):
        """Create a random quantity of product for every non-root category."""
        for c in Category.objects.exclude(parent=None):
            for i in range(1, randint(10, 50)):
                Product.objects.create(
                    name='Product of {}'.format(c),
                    price=i * randint(1, 100),
                    category=c,
                    wholesale_small=10,
                    wholesale_medium=10,
                    wholesale_large=10,
                )

    def clear_tables(self):
        """Remove everything from Category and Product tables."""
        Category.objects.all().delete()
        Product.objects.all().delete()
