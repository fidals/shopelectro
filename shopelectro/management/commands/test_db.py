"""
Create serialized data for tests.
Store this data in json file.

Usage:
- create db named `test`
- fix your settings.DATABASES option
- purge your test db manually, if it had data before this usage
- launch this command
- now you have json file, that'll be used by our TDD tests
"""

from itertools import chain
import os
from random import randint

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management import call_command
from django.core.management.base import BaseCommand

from images.models import Image
from pages.models import Page, FlatPage
from pages.utils import save_custom_pages, init_redirects_app

from shopelectro.models import Product, Category, Order, ProductFeedback
import shopelectro.tests


class Command(BaseCommand):

    FIRST_IMAGE = os.path.join(
        os.path.dirname(os.path.abspath(shopelectro.tests.__file__)),
        'assets/deer.jpg'
    )
    SECOND_IMAGE = os.path.join(
        os.path.dirname(os.path.abspath(shopelectro.tests.__file__)),
        'assets/gold_deer.jpg'
    )
    PRODUCT_WITH_IMAGE = 1

    def __init__(self):
        super(BaseCommand, self).__init__()
        self._product_id = 0

    def handle(self, *args, **options):
        self.prepare_db()
        save_custom_pages()
        init_redirects_app()

        roots = self.create_root(2)
        children = self.create_children(2, roots)
        deep_children = self.create_children(2, children)

        self.create_products(list(deep_children))
        self.create_page()
        self.create_order()
        self.create_feedbacks()
        self.save_dump()

    def prepare_db(self):
        assert settings.DATABASES['default']['NAME'] == 'test'
        call_command('migrate')
        self.purge_tables()

    @staticmethod
    def save_dump():
        """Save .json dump to fixtures."""
        call_command(
            'dumpdata',
            '--all',
            # I don't understand why we should use this options.
            # As well as ContentType model above.
            # I just followed this: http://bit.ly/so-contenttype-dump-solving
            '--natural-foreign',
            '--natural-primary',
            output='shopelectro/fixtures/dump.json'
        )

    @staticmethod
    def create_root(count):
        get_name = 'Category #{}'.format
        return [Category.objects.create(name=get_name(i)) for i in range(count)]

    @property
    def product_id(self):
        self._product_id += 1
        return self._product_id

    @staticmethod
    def create_children(count, parents):
        name = 'Category #{} of #{}'

        def create_categories(name, parent):
            return Category.objects.create(name=name, parent=parent)

        def get_name(number, parent=None):
            return name.format(number, parent)

        return chain.from_iterable(
            [create_categories(get_name(i, parent), parent) for i in range(count)]
            for parent in parents
        )

    def create_products(self, categories):
        """Fill given categories with products"""

        def create_images(page: Page):
            def create_image(file_path, slug):
                Image.objects.create(
                    model=page,
                    slug=slug,
                    image=ImageFile(open(file_path, mode='rb'))
                )

            create_image(file_path=self.FIRST_IMAGE, slug='deer')
            create_image(file_path=self.SECOND_IMAGE, slug='gold')

        def create_product(parent: Category, price_factor):
            product = Product.objects.create(
                id=self.product_id,
                name='Product #{} of {}'.format(price_factor, parent),
                price=price_factor * 100,
                category=parent,
                wholesale_small=price_factor * 75,
                wholesale_medium=price_factor * 50,
                wholesale_large=price_factor * 25
            )
            if product.id == self.PRODUCT_WITH_IMAGE:
                create_images(product.page)

        def fill_with_products(to_fill, count):
            for category in to_fill:
                for i in range(1, count + 1):
                    create_product(category, price_factor=i)

        fill_with_products(to_fill=categories[4:], count=25)
        fill_with_products(to_fill=categories[:4], count=50)

    @staticmethod
    def create_page():
        """Create only one page with type=FLAT_PAGE"""
        FlatPage.objects.create(
            slug='flat',
        )

    @staticmethod
    def create_order():
        Order.objects.create(
            pk=7,
            name='Test Name',
            phone='88005553535',
        )

    @staticmethod
    def create_feedbacks():
        feedbacks_count = 5

        def generate_feedback_data(index):
            return {
                'product': Product.objects.get(id=1),
                'rating': index,
                'user_name': 'User #{}'.format(index),
                'dignities': 'Some dignities.',
                'limitations': 'Some limitations.',
                'general': 'Some general opinion.'
            }

        for i in range(feedbacks_count):
            ProductFeedback.objects.create(**generate_feedback_data(i + 1))

    @staticmethod
    def purge_tables():
        call_command('flush', '--noinput')
