from math import ceil

from django.test import TestCase

from shopelectro.cart import SECart
from shopelectro.config import PRICE_BOUNDS
from shopelectro.models import Product


class SECartTest(TestCase):

    fixtures = ['dump.json']

    def __init__(self, *args, **kwargs):
        self.item_quantity = 2
        super().__init__(*args, **kwargs)

    def setUp(self):
        """Get session for test."""
        self.products = Product.objects.all()[:self.item_quantity]
        self.first_product, self.second_product = self.products
        self.session = self.client.session

    @property
    def cart(self):
        """Return Cart object for test."""
        return SECart(self.session)

    @staticmethod
    def get_price(product, price_type):
        return float(getattr(product, price_type))

    def get_wholesale_data(self, price_type, products: list):
        """
        Return minimal products count, that we should put in cart to get
        assigned price_type.
        """
        bound_devider = len(products)
        wholesale_price_type = {
            'wholesale_large': PRICE_BOUNDS['wholesale_large'],
            'wholesale_medium': PRICE_BOUNDS['wholesale_medium'],
            'wholesale_small': PRICE_BOUNDS['wholesale_small'],
            'price': 10000
        }

        def get_data(product):
            price = self.get_price(product, price_type)
            quantity = ceil(
                wholesale_price_type[price_type] / bound_devider / price)
            return {
                'price': price,
                'quantity': quantity
            }

        wholesale_data = {product: get_data(product) for product in products}
        *_, last_product = products
        # Increment quantity, because wholesale price should be strictly
        # more then bounds.
        wholesale_data[last_product]['quantity'] += 1

        return wholesale_data

    def setup_for_tests(self, price_type):
        product_data = (
            self.get_wholesale_data(
                price_type,
                [self.first_product, self.second_product],
            )
        )

        first_product = product_data[self.first_product]
        second_product = product_data[self.second_product]

        total_sum = (
            first_product['price'] * first_product['quantity'] +
            second_product['price'] * second_product['quantity']
        )

        return {
            'first_product_price': first_product['price'],
            'second_product_price': second_product['price'],
            'first_product_quantity': first_product['quantity'],
            'second_product_quantity': second_product['quantity'],
            'total_sum': total_sum
        }

    def setup_for_before_and_after_test(self, before, after):
        before = self.setup_for_tests(before)
        after = self.setup_for_tests(after)
        self.cart.add(
            self.first_product, before['first_product_quantity']
        )
        self.cart.add(
            self.second_product, before['second_product_quantity']
        )
        return before, after

    def get_total_sum_for_set_product_quantity(self, before, after):
        return (
            after['first_product_price'] * before['first_product_quantity'] +
            after['second_product_price'] * after['second_product_quantity']
        )

    def get_total_sum_for_remove_method(self, before, after):
        return (
            after['first_product_price'] *
            before['first_product_quantity']
        )

    def run_add_test(self, data):
        self.cart.add(
            self.first_product,
            data['first_product_quantity']
        )
        self.cart.add(
            self.second_product,
            data['second_product_quantity']
        )
        prices = [
            data['first_product_price'],
            data['second_product_price']
        ]
        for _, position in self.cart:
            self.assertIn(position['price'], prices)

        self.assertEqual(data['total_sum'], self.cart.total_price)

    def run_set_test(self, before, after):
        total_sum = self.get_total_sum_for_set_product_quantity(before, after)
        self.cart.set_product_quantity(
            self.second_product,
            after['second_product_quantity']
        )
        self.assertEqual(
            total_sum, self.cart.total_price
        )

    def run_remove_test(self, before, after):
        total_sum = self.get_total_sum_for_remove_method(before, after)
        self.cart.set_product_quantity(
            self.second_product,
            after['second_product_quantity']
        )
        self.assertEqual(
            total_sum, self.cart.total_price
        )

    def test_add_method_for_wholesale_small(self):
        """
        If the sum of prices on small wholesale is greater than
        20 000 rub. then price for every product equated small wholesale price.
        """
        self.run_test(self.setup_for_tests('wholesale_small'))

    def test_add_method_for_wholesale_medium(self):
        """
        If the sum of prices on medium wholesale is greater than
        50 000 rub. then price for every product equated medium
        wholesale price.
        """
        self.run_test(self.setup_for_tests('wholesale_medium'))

    def test_add_method_for_wholesale_large(self):
        """
        If the sum of prices on large wholesale is greater than
        100 000 rub. then price for every product equated large
        wholesale price.
        """
        self.run_test(self.setup_for_tests('wholesale_large'))

    def test_remove_method_for_wholesale_small(self):
        """
        If the sum of prices on small wholesale is less than
        15 000 rub. then price for every product equated default price.
        """
        self.run_remove_test(*self.setup_for_before_and_after_test(
            'wholesale_small', 'price'
        ))

    def test_remove_method_for_wholesale_medium(self):
        """
        If the sum of prices on medium wholesale is less than
        40 000 rub. then price for every product equated small price.
        """
        self.run_remove_test(*self.setup_for_before_and_after_test(
            'wholesale_medium', 'wholesale_small'
        ))

    def test_remove_method_for_wholesale_large(self):
        """
        If the sum of prices on large wholesale is less than
        100 000 rub. then price for every product equated medium price.
        """
        self.run_remove_test(*self.setup_for_before_and_after_test(
            'wholesale_large', 'wholesale_medium'
        ))

    def test_set_product_quantity_method_for_wholesale_small(self):
        """
        If the sum of prices on small wholesale is less than
        15 000 rub. then price for every product equated default price.
        """
        self.run_set_test(*self.setup_for_before_and_after_test(
            'wholesale_small', 'price'
        ))

    def test_set_product_quantity_method_for_wholesale_medium(self):
        """
        If the sum of prices on medium wholesale is less than
        40 000 rub. then price for every product equated small price.
        """
        self.run_set_test(*self.setup_for_before_and_after_test(
            'wholesale_medium', 'wholesale_small'
        ))

    def test_set_product_quantity_method_for_wholesale_large(self):
        """
        If the sum of prices on large wholesale is less than
        40 000 rub. then price for every product equated medium price.
        """
        self.run_set_test(*self.setup_for_before_and_after_test(
            'wholesale_large', 'wholesale_medium'
        ))
