from math import ceil

from django.test import TestCase

from shopelectro.models import Product
from shopelectro.cart import WholesaleCart


class WholesaleCartTest(TestCase):

    fixtures = ['dump.json']

    def __init__(self, *args, **kwargs):
        self.item_quantity = 2

        super(WholesaleCartTest, self).__init__(*args, **kwargs)

    def setUp(self):
        """Get session for test."""
        self.products = Product.objects.all()[:self.item_quantity]
        self.first_product, self.second_product = self.products
        self.session = self.client.session

    @property
    def cart(self):
        """Return Cart object for test."""
        return WholesaleCart(self.session)

    def get_wholesale_quantity(self, price_type, product):
        """
        Return the approximate number of products with wholesale price type for
        tests.
        """
        wholesale_price_type = {
            'price': 14000,
            'wholesale_large': 100000,
            'wholesale_medium': 50000,
            'wholesale_small': 20000,
        }

        return ceil(
                wholesale_price_type[price_type] /
                getattr(product, price_type) /
                self.item_quantity
        ) + 1

    def setup_for_tests(self, price_type):
        first_product_price = float(getattr(self.first_product, price_type))
        second_product_price = float(getattr(self.second_product, price_type))

        first_product_quantity = (
            self.get_wholesale_quantity(price_type, self.first_product)
        )

        second_product_quantity = (
            self.get_wholesale_quantity(price_type, self.second_product)
        )

        total_sum = (
            first_product_price*first_product_quantity +
            second_product_price*second_product_quantity
        )

        return {
            'first_product_price': first_product_price,
            'second_product_price': second_product_price,
            'first_product_quantity': first_product_quantity,
            'second_product_quantity': second_product_quantity,
            'total_sum': total_sum
        }

    def test_add_method_for_wholesale_small(self):
        """
        If the sum of prices on small wholesale is greater than
        20 000 rub. then price for every product equated small wholesale price.
        """
        setup_data = self.setup_for_tests('wholesale_small')

        self.cart.add(self.first_product,
                      setup_data['first_product_quantity'])
        self.cart.add(self.second_product,
                      setup_data['second_product_quantity'])
        for id_, position in self.cart:
            self.assertIn(
                position['price'],
                [setup_data['first_product_price'], setup_data['second_product_price']]
            )

        self.assertEqual(setup_data['total_sum'], self.cart.total_price)

    def test_add_method_for_wholesale_medium(self):
        """
        If the sum of prices on medium wholesale is greater than
        50 000 rub. then price for every product equated medium wholesale price.
        """
        setup_data = self.setup_for_tests('wholesale_medium')

        self.cart.add(self.first_product, setup_data['first_product_quantity'])
        self.cart.add(self.second_product, setup_data['second_product_quantity'])

        for id_, position in self.cart:
            self.assertIn(
                position['price'],
                [setup_data['first_product_price'],
                 setup_data['second_product_price']]
            )
        self.assertEqual(setup_data['total_sum'], self.cart.total_price)

    def test_add_method_for_wholesale_large(self):
        """
        If the sum of prices on large wholesale is greater than
        100 000 rub. then price for every product equated large wholesale price.
        """
        setup_data = self.setup_for_tests('wholesale_large')

        self.cart.add(self.first_product, setup_data[
            'first_product_quantity'])
        self.cart.add(self.second_product, setup_data[
            'second_product_quantity'])

        for id_, position in self.cart:
            self.assertIn(position['price'],
                          [setup_data['first_product_price'],
                           setup_data['second_product_price']])
        self.assertEqual(setup_data['total_sum'],
                         self.cart.total_price)

    def setup_for_remove_method(self, before, after):
        before = self.setup_for_tests(before)
        after = self.setup_for_tests(after)
        self.cart.add(self.first_product,
                      before['first_product_quantity'])
        self.cart.add(self.second_product,
                      before['second_product_quantity'])
        total_sum = (after['first_product_price'] *
                     before['first_product_quantity'])

        return {
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

        self.cart.remove(self.second_product)

        for id_, position in self.cart:
            self.assertEqual(position['price'],
                             setup_data['after']['first_product_price'])
        self.assertEqual(setup_data['total_sum'],
                         self.cart.total_price)

    def test_remove_method_for_wholesale_medium(self):
        """
        If the sum of prices on medium wholesale is less than
        40 000 rub. then price for every product equated small price.
        """
        setup_data = self.setup_for_remove_method('wholesale_medium',
                                                  'wholesale_small')

        self.cart.remove(self.second_product)

        for id_, position in self.cart:
            self.assertEqual(position['price'],
                             setup_data['after']['first_product_price'])
        self.assertEqual(setup_data['total_sum'],
                         self.cart.total_price)

    def test_remove_method_for_wholesale_large(self):
        """
        If the sum of prices on large wholesale is less than
        100 000 rub. then price for every product equated medium price.
        """
        setup_data = self.setup_for_remove_method('wholesale_large',
                                                  'wholesale_medium')

        self.cart.remove(self.second_product)

        for id_, position in self.cart:
            self.assertEqual(position['price'],
                             setup_data['after']['first_product_price'])
        self.assertEqual(setup_data['total_sum'],
                         self.cart.total_price)

    def setup_for_set_product_quantity(self, before, after):
        before = self.setup_for_tests(before)
        after = self.setup_for_tests(after)
        self.cart.add(self.first_product,
                      before['first_product_quantity'])
        self.cart.add(self.second_product,
                      before['second_product_quantity'])
        total_sum = (after['first_product_price'] *
                     before['first_product_quantity'] +
                     after['second_product_price'] *
                     after['second_product_quantity'])

        return {
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

        self.cart.set_product_quantity(
            self.second_product,
            setup_data['after']['second_product_quantity']
        )

        self.assertEqual(setup_data['total_sum'],
                         self.cart.total_price)

    def test_set_product_quantity_method_for_wholesale_medium(self):
        """
        If the sum of prices on medium wholesale is less than
        40 000 rub. then price for every product equated small price.
        """
        setup_data = self.setup_for_set_product_quantity(
            'wholesale_medium', 'wholesale_small'
        )

        self.cart.set_product_quantity(
            self.second_product,
            setup_data['after']['second_product_quantity']
        )

        self.assertEqual(setup_data['total_sum'],
                         self.cart.total_price)

    def test_set_product_quantity_method_for_wholesale_large(self):
        """
        If the sum of prices on large wholesale is less than
        40 000 rub. then price for every product equated medium price.
        """
        setup_data = self.setup_for_set_product_quantity(
            'wholesale_large', 'wholesale_medium'
        )

        self.cart.set_product_quantity(
            self.second_product,
            setup_data['after']['second_product_quantity']
        )

        self.assertEqual(setup_data['total_sum'],
                         self.cart.total_price)
