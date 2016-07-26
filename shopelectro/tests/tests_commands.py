"""
Tests for catalog command, which call other commands like price and excel.

Note: tests running pretty long.
"""

import os
import types

from collections import namedtuple
from xml.etree import ElementTree

from django.core.management import call_command
from django.conf import settings
from django.test import TestCase

from shopelectro.models import Product, Category
from shopelectro.management.commands import catalog


class ImportTest(TestCase):
    # TODO: testing XMLs are needed

    @classmethod
    def setUpTestData(cls):
        call_command('catalog')
        cls.test_product_id = 293
        cls.test_category_id = 2  # Accumulators category

    @classmethod
    def tearDownClass(cls):
        super(ImportTest, cls).tearDownClass()
        os.remove('priceru.xml')
        os.remove('pricelist.xlsx')
        os.remove('yandex.yml')

    def test_removed_files(self):
        """After performing command there should be no files."""
        self.assertNotIn('products.xml', os.listdir(settings.BASE_DIR))

    def test_parse_return_generator_with_product_instances(self):
        """Parsing methods should return generator object."""
        command = catalog.Command()
        command.get_xml_files()
        product_generator = command.parse_products()
        categories_generator = command.parse_categories()
        self.assertIsInstance(product_generator, types.GeneratorType)
        self.assertIsInstance(categories_generator, types.GeneratorType)
        command.remove_xml()

    def test_products_in_db(self):
        """Should be more than 3K products in DB."""
        products = Product.objects.all()
        self.assertGreaterEqual(len(products), 3000)

    def test_product_has_all_fields(self):
        """Some product has all the fields."""
        product = Product.objects.get(id=self.test_product_id)
        self.assertIsNotNone(product.id)
        self.assertIsNotNone(product.category)
        self.assertIsNotNone(product.price)
        self.assertIsNotNone(product.wholesale_small)
        self.assertIsNotNone(product.wholesale_medium)
        self.assertIsNotNone(product.wholesale_large)

    def test_categories_in_db(self):
        """Should be more than 140 categories in DB."""
        categories = Category.objects.all()
        self.assertGreaterEqual(len(categories), 140)

    def test_category_has_all_fields(self):
        """Some product has all the fields."""
        category = Category.objects.get(id=self.test_category_id)
        self.assertIsNotNone(category.id)
        self.assertIsNotNone(category.children)
        self.assertIsNotNone(category.position)

    def test_prices_exists(self):
        """Catalog command should generate various price-list files."""
        File = namedtuple('File', ['name', 'size'])
        price_files = [File('pricelist.xlsx', 200 * 1000),
                       File('yandex.yml', 3 * 1000000),
                       File('priceru.xml', 3 * 1000000)]
        for file in price_files:
            self.assertIn(file.name, os.listdir(settings.BASE_DIR))
            size = os.stat(file.name).st_size
            self.assertGreaterEqual(size, file.size)

    def test_categories_in_price(self):
        """There should be at least 60 categories in price. (except Others)"""
        categories_in_price = ElementTree.parse(
            'priceru.xml').getroot().find('shop').find('categories')
        self.assertGreaterEqual(len(categories_in_price), 60)

    def test_products_in_price(self):
        """There should be at least 2000 products in price. (except Others)"""
        products_in_price = ElementTree.parse(
            'priceru.xml').getroot().find('shop').find('offers')
        self.assertGreaterEqual(len(products_in_price), 2000)

    def test_no_others_categories_in_price(self):
        """There should be no categories inherited from Other category."""
        others = Category.objects.get(name='Прочее').get_descendants(
            include_self=True).values('id')
        categories_in_price = ElementTree.parse(
            'priceru.xml').getroot().find('shop').find('categories')
        for category in categories_in_price:
            self.assertFalse(category.attrib['id'] in others.values())

    def test_no_others_products_in_price(self):
        """There should be no products from Other category and its children."""
        others = Category.objects.get(
            name='Прочее').get_descendants(include_self=True)
        products_others = Product.objects.filter(
            category__in=others).values('id')
        products_in_price = ElementTree.parse(
            'priceru.xml').getroot().find('shop').find('offers')
        for product in products_in_price:
            self.assertFalse(product.attrib['id'] in products_others.values())
