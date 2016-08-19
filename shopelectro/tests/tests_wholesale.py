from math import ceil

from django.test import TestCase

from shopelectro.models import Product, Category
from shopelectro.cart import WholesaleCart


class WholesaleCartTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create products and category for them."""
        category = Category.objects.create(name='Test')
        cls.item_quantity = 2
        cls.products = cls.first_product, cls.second_product = [
            Product.objects.create(
                name='Product {}'.format(i),
                category=category,
                price='1550.00',
                wholesale_small='1145.74',
                wholesale_medium='1082.59',
                wholesale_large='992.38'
            ) for i in range(cls.item_quantity)
        ]

    def setUp(self):
        """Get session for test."""
        self.session = self.client.session

    @property
    def cart(self):
        """Return Cart object for test."""
        return WholesaleCart(self.session)

    def wholesale_quantity(self, price_type):
        """
        Return the approximate number of products with wholesale price type for
        tests.
        """
        wholesale_price_type = {
            'price': 14000,
            'wholesale_small': 15000,
            'wholesale_medium': 40000,
            'wholesale_large': 100000
        }
        return sum(
            ceil(wholesale_price_type[price_type] /
                 float(getattr(product, price_type)) /
                 self.item_quantity)
            for product in self.products
        )

    def setup_for_tests(self, price_type):
        first_product_price = float(getattr(self.first_product, price_type))
        second_product_price = float(getattr(self.second_product, price_type))
        first_product_quantity = (self.wholesale_quantity(price_type) //
                                  self.item_quantity)
        second_product_quantity = (self.wholesale_quantity(price_type) -
                                   first_product_quantity)
        total_sum = (first_product_price * first_product_quantity +
                     second_product_price * second_product_quantity)

        return {
            'cart': self.cart,
            'first_product_price': first_product_price,
            'second_product_price': second_product_price,
            'first_product_quantity': first_product_quantity,
            'second_product_quantity': second_product_quantity,
            'total_sum': total_sum
        }

    def test_add_method_for_wholesale_small(self):
        """
        If the sum of prices on small wholesale is greater than
        15 000 rub. then price for every product equated small wholesale price.
        """
        setup_data = self.setup_for_tests('wholesale_small')

        setup_data['cart'].add(self.first_product,
                               setup_data['first_product_quantity'])
        setup_data['cart'].add(self.second_product,
                               setup_data['second_product_quantity'])

        for item in setup_data['cart']:
            self.assertIn(item['price'], [setup_data['first_product_price'],
                                          setup_data['second_product_price']])
        self.assertEqual(setup_data['total_sum'],
                         setup_data['cart'].total_price)

    def test_add_method_for_wholesale_medium(self):
        """
        If the sum of prices on medium wholesale is greater than
        40 000 rub. then price for every product equated medium wholesale price.
        """
        setup_data = self.setup_for_tests('wholesale_medium')

        setup_data['cart'].add(self.first_product,
                               setup_data['first_product_quantity'])
        setup_data['cart'].add(self.second_product,
                               setup_data['second_product_quantity'])

        for item in setup_data['cart']:
            self.assertIn(
                item['price'],
                [setup_data['first_product_price'],
                 setup_data['second_product_price']]
            )
        self.assertEqual(setup_data['total_sum'],
                         setup_data['cart'].total_price)

    def test_add_method_for_wholesale_large(self):
        """
        If the sum of prices on large wholesale is greater than
        100 000 rub. then price for every product equated large wholesale price.
        """
        setup_data = self.setup_for_tests('wholesale_large')

        setup_data['cart'].add(self.first_product, setup_data[
                               'first_product_quantity'])
        setup_data['cart'].add(self.second_product, setup_data[
                               'second_product_quantity'])

        for item in setup_data['cart']:
            self.assertIn(item['price'],
                          [setup_data['first_product_price'],
                           setup_data['second_product_price']])
        self.assertEqual(setup_data['total_sum'],
                         setup_data['cart'].total_price)

    def setup_for_remove_method(self, before, after):
        before = self.setup_for_tests(before)
        after = self.setup_for_tests(after)
        before['cart'].add(self.first_product,
                           before['first_product_quantity'])
        before['cart'].add(self.second_product,
                           before['second_product_quantity'])
        total_sum = (after['first_product_price'] *
                     before['first_product_quantity'])

        return {
            'cart': before['cart'],
            'total_sum': total_sum,
            'before': before,
            'after': after
        }

    def test_remove_method_for_wholesale_small(self):
        """
        If the sum of prices on small wholesale is less than
        15 000 rub. then price for every product equated default price.
        """
        setup_data = self.setup_for_remove_method('wholesale_small', 'price')

        setup_data['cart'].remove(self.second_product)

        for item in setup_data['cart']:
            self.assertEqual(item['price'],
                             setup_data['after']['first_product_price'])
        self.assertEqual(setup_data['total_sum'],
                         setup_data['cart'].total_price)

    def test_remove_method_for_wholesale_medium(self):
        """
        If the sum of prices on medium wholesale is less than
        40 000 rub. then price for every product equated small price.
        """
        setup_data = self.setup_for_remove_method('wholesale_medium',
                                                  'wholesale_small')

        setup_data['cart'].remove(self.second_product)

        for item in setup_data['cart']:
            self.assertEqual(item['price'],
                             setup_data['after']['first_product_price'])
        self.assertEqual(setup_data['total_sum'],
                         setup_data['cart'].total_price)

    def test_remove_method_for_wholesale_large(self):
        """
        If the sum of prices on large wholesale is less than
        100 000 rub. then price for every product equated medium price.
        """
        setup_data = self.setup_for_remove_method('wholesale_large',
                                                  'wholesale_medium')

        setup_data['cart'].remove(self.second_product)

        for item in setup_data['cart']:
            self.assertEqual(item['price'],
                             setup_data['after']['first_product_price'])
        self.assertEqual(setup_data['total_sum'],
                         setup_data['cart'].total_price)

    def setup_for_set_product_quantity(self, before, after):
        before = self.setup_for_tests(before)
        after = self.setup_for_tests(after)
        before['cart'].add(self.first_product,
                           before['first_product_quantity'])
        before['cart'].add(self.second_product,
                           before['second_product_quantity'])
        total_sum = (after['first_product_price'] *
                     before['first_product_quantity'] +
                     after['second_product_price'] *
                     after['second_product_quantity'])

        return {
            'cart': before['cart'],
            'total_sum': total_sum,
            'before': before,
            'after': after
        }

    def test_set_product_quantity_method_for_wholesale_small(self):
        """
        If the sum of prices on small wholesale is less than
        15 000 rub. then price for every product equated default price.
        """
        setup_data = self.setup_for_set_product_quantity(
            'wholesale_small', 'price'
        )

        setup_data['cart'].set_product_quantity(
            self.second_product,
            setup_data['after']['second_product_quantity']
        )

        self.assertEqual(setup_data['total_sum'],
                         setup_data['cart'].total_price)

    def test_set_product_quantity_method_for_wholesale_medium(self):
        """
        If the sum of prices on medium wholesale is less than
        40 000 rub. then price for every product equated small price.
        """
        setup_data = self.setup_for_set_product_quantity(
            'wholesale_medium', 'wholesale_small'
        )

        setup_data['cart'].set_product_quantity(
            self.second_product,
            setup_data['after']['second_product_quantity']
        )

        self.assertEqual(setup_data['total_sum'],
                         setup_data['cart'].total_price)

    def test_set_product_quantity_method_for_wholesale_large(self):
        """
        If the sum of prices on large wholesale is less than
        40 000 rub. then price for every product equated medium price.
        """
        setup_data = self.setup_for_set_product_quantity(
            'wholesale_large', 'wholesale_medium'
        )

        setup_data['cart'].set_product_quantity(
            self.second_product,
            setup_data['after']['second_product_quantity']
        )

        self.assertEqual(setup_data['total_sum'],
                         setup_data['cart'].total_price)
