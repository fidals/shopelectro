"""
Tests for catalog command, which call other commands like price and excel.

Note: tests running pretty long.
"""
import glob
import os
import random
import uuid
from xml.etree import ElementTree

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from shopelectro.management.commands import price
from shopelectro.management.commands._update_catalog import (
    update_products, update_tags
)
from shopelectro.models import (
    Category, Product, ProductPage, CategoryPage, Tag, TagGroup
)


class UpdateProducts(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('update_catalog', '--recipients', 'username@example.com')
        super(UpdateProducts, cls).setUpTestData()

    def test_products_in_db(self):
        """Should be more than 3K products in DB."""
        self.assertGreaterEqual(Product.objects.count(), 3000)

    def test_product_has_all_fields(self):
        """Some product has all the fields."""
        product = random.choice(Product.objects.all())
        self.assertIsNotNone(product.id)
        self.assertIsNotNone(product.vendor_code)
        self.assertIsNotNone(product.price)
        self.assertIsNotNone(product.wholesale_small)
        self.assertIsNotNone(product.wholesale_medium)
        self.assertIsNotNone(product.wholesale_large)

    def test_delete_xml(self):
        """Delete XML files after process"""
        file_paths = glob.glob(
            os.path.join(settings.ASSETS_DIR, settings.FTP_IP, '**/*.xml'),
            recursive=True
        )

        self.assertEqual(len(file_paths), 0)

    def test_update_produts(self):
        new_data = {'price': 123}
        update_products_count = 30

        product_data = {
            str(product.uuid): new_data
            for product in Product.objects.all()[:update_products_count]
        }

        update_products.update(data=product_data)
        updated_products = Product.objects.filter(**new_data)

        self.assertEqual(len(updated_products), update_products_count)
        self.assertTrue(all(
            product.price == new_data['price']
            for product in updated_products))

    def test_create_products(self):
        create_count = 10
        tag_count = 2

        data = {
            'name': 'New product',
            'vendor_code': '123',
            'tags': Tag.objects.all()[:tag_count]
        }

        product_data = {
            str(uuid.uuid4()): data
            for _ in range(create_count)
        }

        updated_products = Product.objects.all()
        product_count = updated_products.count()

        update_products.create(data=product_data, updated_products=updated_products)

        self.assertEqual(product_count + create_count, Product.objects.count())
        self.assertEqual(create_count, Product.objects.filter(name=data['name']).count())

    def test_delete_products(self):
        save_product_count = 30

        product_data = {
            str(product.uuid): 'any data'
            for product in Product.objects.all()[:save_product_count]
        }

        update_products.delete(data=product_data)

        self.assertEqual(Product.objects.count(), save_product_count)

    def test_update_or_create_tags(self):
        create_count = 10
        tag_data = {
            str(uuid.uuid4()): {
                'name': 'New group',
                'tags': {uuid.uuid4(): {'name': 'New tag'}}
            } for _ in range(create_count)
        }

        updated_groups_count = TagGroup.objects.count()
        updated_tags_count = Tag.objects.count()

        update_tags.create_or_update(tag_data)

        self.assertEqual(updated_groups_count + create_count, TagGroup.objects.count())
        self.assertEqual(updated_tags_count + create_count, Tag.objects.count())

    def test_delete_tags(self):
        groups_count = 2

        tag_data = {
            str(group.uuid): {
                'name': 'some name',
                'tags': {
                    tag.uuid: {'name': tag.name}
                    for tag in Tag.objects.filter(group=group)
                }
            } for group in TagGroup.objects.all()[:groups_count]
        }

        tag_count = sum(len(data['tags']) for data in tag_data.values())

        update_tags.delete(tag_data)

        self.assertEqual(Tag.objects.count(), tag_count)
        self.assertEqual(TagGroup.objects.count(), groups_count)


class UpdateMetaTags(TestCase):

    fixtures = ['dump.json']

    @staticmethod
    def have_just_filled_fields(pages, fields):
        """Pages have filled fields."""
        def is_filled(page, value):
            return value != page.name and value is not None

        return all(
            is_filled(page, getattr(page, field))
            for page in pages for field in fields
        )

    def _test_pattern(self, model, fields):
        pages = model.objects.all()
        self.assertFalse(self.have_just_filled_fields(pages, fields))

        call_command('update_meta_tags')

        updated_pages = model.objects.all()
        self.assertTrue(self.have_just_filled_fields(updated_pages, fields))

    def test_update_product(self):
        self._test_pattern(ProductPage, ['title', 'description'])

    def test_update_category(self):
        self._test_pattern(CategoryPage, ['seo_text', 'title'])


class GeneratePrices(TestCase):

    fixtures = ['dump.json']

    @classmethod
    def setUpTestData(cls):
        call_command('price')
        super(GeneratePrices, cls).setUpTestData()

    @classmethod
    def tearDownClass(cls):
        for file_name in price.Command.TARGETS.values():
            os.remove(cls.get_price_file_path(file_name))
        super(GeneratePrices, cls).tearDownClass()

    @staticmethod
    def get_price_file_path(filename):
        return os.path.join(settings.ASSETS_DIR, filename)

    @classmethod
    def get_price_xml_node(cls):
        return ElementTree.parse(cls.get_price_file_path('priceru.xml'))

    def test_prices_exists(self):
        """Price command should generate various price-list files."""
        price_file_min_size = 10 ** 4  # ~10kb

        for name in price.Command.TARGETS.values():
            file_name = self.get_price_file_path(name)
            self.assertIn(name, os.listdir(settings.ASSETS_DIR))
            size = os.stat(file_name).st_size
            self.assertGreaterEqual(size, price_file_min_size)

    def test_categories_in_price(self):
        categories_in_price = self.get_price_xml_node().getroot().find('shop').find('categories')
        self.assertEqual(len(categories_in_price), Category.objects.count())

    def test_products_in_price(self):
        products_in_price = self.get_price_xml_node().getroot().find('shop').find('offers')
        self.assertEqual(len(products_in_price), Product.objects.count())
