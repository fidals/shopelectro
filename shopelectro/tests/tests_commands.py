"""
Tests for catalog command, which call other commands like price and excel.

Note: tests running pretty long.
"""
import os
import types

from xml.etree import ElementTree

from django.core.management import call_command
from django.conf import settings
from django.test import TestCase

from shopelectro.models import Product, Category
from shopelectro.management.commands import catalog


# TODO - we should create (use) fixture db
# http://bit.ly/refarm_tail_fixture_db4command
class ImportTest(TestCase):

    TEST_CATEGORY_ID = 2
    TEST_PRODUCT_ID = 293
    PRICE_FILES = ['priceru.xml', 'pricelist.xlsx', 'yandex.yml', 'gm.yml']

    @staticmethod
    def get_price_file_path(filename):
        return os.path.join(settings.ASSETS_DIR, filename)

    @staticmethod
    def get_price_xml_node():
        return ElementTree.parse(ImportTest.get_price_file_path('priceru.xml'))

    @classmethod
    def setUpTestData(cls):
        cls.test_product_id = 293
        cls.test_category_id = 2  # Accumulators category

        cls.category_for_update = Category.objects.create(
            id=cls.test_category_id, name='FOR UPDATE')
        cls.product_for_update = Product.objects.create(
            id=cls.test_product_id,
            name='FOR UPDATE',
            category=cls.category_for_update,
            price=123,
            wholesale_small=123,
            wholesale_medium=123,
            wholesale_large=123,
        )

        cls.id_for_delete = 324132222
        category_for_delete = Category.objects.create(id=cls.id_for_delete, name='FOR DELETE')
        Product.objects.create(
            id=cls.id_for_delete,
            name='FOR DELETE',
            category=category_for_delete,
            price=123,
            wholesale_small=123,
            wholesale_medium=123,
            wholesale_large=123,
        )

        def get_test_yml_product():
            for product in products:
                if product.attrib['id'] == str(cls.TEST_PRODUCT_ID):
                    return product

        call_command('catalog')
        products = cls.get_price_xml_node().getroot().find('shop').find('offers')

        cls.test_yml_product = get_test_yml_product()

    @classmethod
    def tearDownClass(cls):
        super(ImportTest, cls).tearDownClass()
        for file_name in cls.PRICE_FILES:
            os.remove(ImportTest.get_price_file_path(file_name))

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
        product = Product.objects.get(id=self.TEST_PRODUCT_ID)
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
        category = Category.objects.get(id=self.TEST_CATEGORY_ID)
        self.assertIsNotNone(category.id)
        self.assertIsNotNone(category.children)
        self.assertIsNotNone(category.page.position)

    def test_prices_exists(self):
        """Catalog command should generate various price-list files."""
        price_file_min_size = 10 ** 4  # ~10kb

        price_names = ['pricelist.xlsx', 'yandex.yml', 'priceru.xml']
        for name in price_names:
            file_name = self.get_price_file_path(name)
            self.assertIn(name, os.listdir(settings.ASSETS_DIR))
            size = os.stat(file_name).st_size
            self.assertGreaterEqual(size, price_file_min_size)

    def test_categories_in_price(self):
        """There should be at least 60 categories in price. (except Others)"""
        categories_in_price = self.get_price_xml_node().getroot().find('shop').find('categories')
        self.assertGreaterEqual(len(categories_in_price), 60)

    def test_products_in_price(self):
        """There should be at least 2000 products in price. (except Others)"""
        products_in_price = self.get_price_xml_node().getroot().find('shop').find('offers')
        self.assertGreaterEqual(len(products_in_price), 1800)

    def test_no_others_categories_in_price(self):
        """There should be no categories inherited from Other category."""
        others = Category.objects.get(name='Прочее').get_descendants(
            include_self=True).values('id')
        categories_in_price = self.get_price_xml_node().getroot().find('shop').find('categories')
        for category in categories_in_price:
            self.assertFalse(category.attrib['id'] in others.values())

    def test_no_others_products_in_price(self):
        """There should be no products from Other category and its children."""
        others = Category.objects.get(
            name='Прочее').get_descendants(include_self=True)
        products_others = Product.objects.filter(
            category__in=others).values('id')
        products_in_price = self.get_price_xml_node().getroot().find('shop').find('offers')
        for product in products_in_price:
            self.assertFalse(product.attrib['id'] in products_others.values())

    def test_update_pages_for_category(self):
        """Every category's page should have a filled title field"""
        category_page = Category.objects.first().page

        test_title = catalog.CATEGORY_TITLE.format(h1=category_page.h1)

        self.assertEqual(test_title, category_page.title)

    def test_update_pages_for_product(self):
        """Every product's page should have a filled title and description field"""
        product = Product.objects.first()
        product_page = product.page

        test_title = catalog.PRODUCT_TITLE.format(h1=product_page.h1)
        test_description = catalog.PRODUCT_DESCRIPTION.format(
            h1=product_page.h1, category_name=product.category.name)

        self.assertEqual(test_title, product_page.title)
        self.assertEqual(test_description, product_page.description)

    def test_exist_products_should_be_updated(self):
        product = Product.objects.get(id=self.test_product_id)

        product_fields = [
            'category', 'price', 'wholesale_small', 'wholesale_medium', 'wholesale_large']
        for field in product_fields:
            self.assertNotEqual(
                getattr(product, field), getattr(self.product_for_update, field))

    def test_exist_categories_should_be_updated(self):
        category = Category.objects.get(id=self.test_category_id)

        category_fields = ['name',]
        for field in category_fields:
            self.assertNotEqual(
                getattr(category, field), getattr(self.category_for_update, field))

    def test_not_exist_products_should_be_deleted(self):
        product = Product.objects.filter(id=self.id_for_delete)

        self.assertFalse(product)

    def test_not_exist_category_should_be_deleted(self):
        category = Category.objects.filter(id=self.id_for_delete)

        self.assertFalse(category)
