"""
Test catalog command, which call other commands like price and excel.

Note: tests running pretty long.
"""
import glob
import os
import random
import typing
import unittest
import urllib.parse
import uuid
from collections import defaultdict
from xml.etree import ElementTree

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings, tag

from shopelectro.management.commands._update_catalog import (
    update_products, update_tags
)
from shopelectro.models import Category, Product, ProductPage, Tag, TagGroup

"""
@todo #179 Раздели тесты класса UpdateProducts на интеграционные и модульные.
 1. Используй файлы с фикстурами для модульных тестов, чтобы добиться стабильности.
 2. Тестируй скачивание файлов с FTP отдельно.
"""


def get_tag_as_dict(group: str, tag: str):
    return {
        str(uuid.uuid4()): {
            'name': group,
            'tags': {uuid.uuid4(): {'name': tag}}
        }
    }


@tag('fast')
class UpdateProductsUnit(TestCase):
    """Unit tests, but not integration."""

    fixtures = ['dump.json']

    def test_product_delete(self):
        """Function called "delete" should not delete, but should deactivate product page."""
        product = Product.objects.first()
        # - delete all products. Our product is among them
        update_products.delete(data={})
        self.assertFalse(product.page.is_active)

    def test_product_pages_consistency(self):
        """Full import cycle with delete/update/create should keep db pages consistency."""
        # - take some existing prod
        product = Product.objects.first()
        product_data = {str(product.uuid): {'name': product.name}}
        # - delete all products. Our product is among them
        update_products.delete(data={})
        # - set our product to db again
        updated_products = update_products.update(product_data)
        update_products.create(product_data, updated_products)
        # - assert if product's page is unique by name
        self.assertEqual(1, ProductPage.objects.filter(name=product.name).count())
        old_named_pages = ProductPage.objects.filter(name=product.name)
        # - and this unique page should be active
        self.assertTrue(old_named_pages.first().is_active)


# @todo #603:30m Resurrect update_catalog tests.
#  Now we have problems with files downloading.
@tag('slow')
@unittest.skip
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
        """Delete XML files after process."""
        file_paths = glob.glob(
            os.path.join(settings.ASSETS_DIR, settings.FTP_IP, '**/*.xml'),
            recursive=True
        )

        self.assertEqual(len(file_paths), 0)

    def test_update_products(self):
        new_data = {'price': 12345.1}
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
            for product in updated_products
        ))

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

    # @todo #452:15m Resurrect delete prods test
    @unittest.expectedFailure
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


class Price:

    def __init__(self, utm: str):
        filename = settings.UTM_PRICE_MAP[utm]
        self.file_path = os.path.join(settings.ASSETS_DIR, filename)
        self.root_node = ElementTree.parse(self.file_path)

    @property
    def shop_node(self) -> ElementTree:
        return self.root_node.getroot().find('shop')

    @property
    def categories_node(self) -> ElementTree:
        return self.shop_node.find('categories')

    @property
    def offers_node(self) -> ElementTree:
        return self.shop_node.find('offers')


class Prices(dict):

    def __init__(self, utm_list: typing.List[str]):
        super().__init__()
        self.update({utm: Price(utm) for utm in utm_list})

    def remove(self):
        """Remove price files."""
        for price in self.values():
            os.remove(price.file_path)


@tag('fast')
class GeneratePrices(TestCase):

    fixtures = ['dump.json']
    CATEGORY_TO_EXCLUDE = 'Category #1 of #Category #0 of #Category #1'
    PRICE_IGNORED_CATEGORIES_MAP = defaultdict(
        list, {'GM': [CATEGORY_TO_EXCLUDE]}
    )
    ignore_categories = override_settings(
        PRICE_IGNORED_CATEGORIES_MAP=PRICE_IGNORED_CATEGORIES_MAP
    )

    @classmethod
    def setUpTestData(cls):
        with cls.ignore_categories:
            call_command('price')
        super(GeneratePrices, cls).setUpTestData()
        cls.prices = Prices(settings.UTM_PRICE_MAP.keys())

    @classmethod
    def tearDownClass(cls):
        cls.prices.remove()
        super(GeneratePrices, cls).tearDownClass()

    def test_prices_exists(self):
        """Price command should generate various price-list files."""
        price_file_min_size = 10 ** 3  # ~1kb

        for utm, filename in settings.UTM_PRICE_MAP.items():
            self.assertIn(filename, os.listdir(settings.ASSETS_DIR))
            size = os.stat(self.prices[utm].file_path).st_size
            self.assertGreaterEqual(size, price_file_min_size)

    def test_categories_in_price(self):
        categories_in_price = self.prices['priceru'].categories_node
        self.assertEqual(len(categories_in_price), Category.objects.count())

    def test_categories_in_yandex_price(self):
        categories = self.prices['YM'].categories_node
        self.assertEqual(
            len(categories),
            Category.objects.get_categories_tree_with_pictures().count()
        )

    @ignore_categories
    def test_categories_excluded_by_utm(self):
        """Price file should not contain it's excluded category."""
        def find_category(categories, name):
            for category in categories:
                if category.text.strip() == name:
                    return category
            return None
        included_name = 'Category #0 of #Category #0 of #Category #1'
        categories_node = self.prices['GM'].categories_node

        # check if find_category inner function is correct
        self.assertIsNotNone(
            find_category(
                categories=categories_node.findall('category'),
                name=included_name
            )
        )
        # check if category excluded
        self.assertIsNone(
            find_category(
                categories=categories_node.findall('category'),
                name=self.CATEGORY_TO_EXCLUDE
            )
        )

    @override_settings(PRICE_IGNORED_PRODUCTS_MAP={'YM': [1, 2, 3]})
    def test_products_excluded_by_id(self):
        to_ignore = set(settings.PRICE_IGNORED_PRODUCTS_MAP['YM'])
        ignored = set(
            offer.attrib['id']
            for offer in self.prices['YM'].offers_node.findall('offer')
        )
        self.assertFalse(to_ignore.intersection(ignored))

    def test_products_in_price(self):
        products = self.prices['priceru'].offers_node
        self.assertEqual(len(products), Product.objects.count())

    def test_products_in_gm_price_bounds(self):
        """GM.yml should contain only offers with price > CONST."""
        offers = self.prices['GM'].offers_node.findall('offer')
        prices_are_in_bounds = all(
            float(offer.find('price').text) > settings.PRICE_GM_LOWER_BOUND
            for offer in offers
        )
        self.assertTrue(prices_are_in_bounds)

    def test_products_in_yandex_price(self):
        products = self.prices['YM'].offers_node
        self.assertEqual(
            len(products),
            Product.objects.filter(page__images__isnull=False).distinct().count()
        )

    def test_brands(self):
        """Price contains brand data."""
        for utm in settings.UTM_PRICE_MAP:
            offer = self.prices[utm].offers_node.find('offer')
            product = Product.objects.filter(id=offer.get('id')).first()
            self.assertEqual(
                product.get_brand_name(),
                offer.find(f'vendor').text,
            )

    def test_utm_yandex(self):
        """Url tag of every offer should contain valid utm marks."""
        offer = self.prices['YM'].offers_node[0]
        url = offer.find('url').text
        get_attrs = urllib.parse.parse_qs(url)
        self.assertEqual('cpc-market', get_attrs['utm_medium'][0])
