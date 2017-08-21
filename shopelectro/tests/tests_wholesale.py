from math import ceil

from django.test import TestCase

from shopelectro.cart import SECart
from shopelectro.config import PRICE_BOUNDS
from shopelectro.models import Product


class SECartTest(TestCase):

    fixtures = ['dump.json']

    def __init__(self, *args, **kwargs):
        self.item_quantity = 2
        self.wholesale_price_type = {
            'wholesale_large': PRICE_BOUNDS['wholesale_large'],
            'wholesale_medium': PRICE_BOUNDS['wholesale_medium'],
            'wholesale_small': PRICE_BOUNDS['wholesale_small'],
            'price': 10000
        }
        super().__init__(*args, **kwargs)

    def setUp(self):
        self.products = Product.objects.all()[:self.item_quantity]
        self.first_product, self.second_product = self.products
        self.session = self.client.session

    @property
    def cart(self):
        """Return Cart object for test."""
        return SECart(self.session)

    def get_wholesale_data(self, price_type, products: list):
        """Return minimal products count to get assigned price_type."""
        bound_devider = len(products)
        def get_data(product):
            price = float(getattr(product, price_type))
            quantity = ceil(
                self.wholesale_price_type[price_type] / bound_devider / price)
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

        return {
            'first_product_price': first_product['price'],
            'second_product_price': second_product['price'],
            'first_product_quantity': first_product['quantity'],
            'second_product_quantity': second_product['quantity'],
        }

    def add_products_to_card(self, data):
        self.cart.add(self.first_product, data['first_product_quantity'])
        self.cart.add(self.second_product, data['second_product_quantity'])
        return data

    def setup_for_before_and_after_test(self, before, after):
        before = self.setup_for_tests(before)
        after = self.setup_for_tests(after)
        return before, after

    def get_set_total(self, before, after):
        return (
            after['first_product_price'] * before['first_product_quantity'] +
            after['second_product_price'] * after['second_product_quantity']
        )

    def get_remove_total(self, before, after):
        return (
            after['first_product_price'] * before['first_product_quantity']
        )

    def get_add_total(self, after):
        return (
            after['first_product_price'] * after['first_product_quantity'] +
            after['second_product_price'] * after['second_product_quantity']
        )

    def run_add_test(self, after, total_sum):
        prices = [
            after['first_product_price'],
            after['second_product_price']
        ]
        for _, position in self.cart:
            self.assertIn(position['price'], prices)
        self.assertEqual(total_sum, self.cart.total_price)

    def run_remove_test(self, after, total_sum):
        for _, position in self.cart:
            self.assertEqual(position['price'], after['first_product_price'])
        self.assertEqual(total_sum, self.cart.total_price)

    def test_add_wholesale_small(self):
        """
        Test changing price type after add product to card.

        If the sum of prices on small wholesale is greater than
        20 000 rub. then price for every product equated small wholesale price.
        """
        after = self.setup_for_tests('wholesale_small')
        self.add_products_to_card(after)
        total = self.get_add_total(after)
        self.run_add_test(after, total)

    def test_add_wholesale_medium(self):
        """
        Test changing price type after add product to card.

        If the sum of prices on medium wholesale is greater than
        50 000 rub. then price for every product equated medium
        wholesale price.
        """
        after = self.setup_for_tests('wholesale_medium')
        self.add_products_to_card(after)
        total = self.get_add_total(after)
        self.run_add_test(after, total)

    def test_add_wholesale_large(self):
        """
        Test changing price type after add product to card.

        If the sum of prices on large wholesale is greater than
        100 000 rub. then price for every product equated large
        wholesale price.
        """
        after = self.setup_for_tests('wholesale_large')
        self.add_products_to_card(after)
        total = self.get_add_total(after)
        self.run_add_test(after, total)

    def test_remove_wholesale_small_to_price(self):
        """
        Test changing price type after remove product from card.

        If the sum of prices on small wholesale is less than
        15 000 rub. then price for every product equated default price.
        """
        before, after = self.setup_for_before_and_after_test(
            'wholesale_small', 'price'
        )
        self.add_products_to_card(before)
        self.cart.remove(self.second_product)
        total = self.get_remove_total(before, after)
        self.run_remove_test(after, total)

    def test_remove_wholesale_medium_to_wholesale_small(self):
        """
        Test changing price type after remove product from card.

        If the sum of prices on medium wholesale is less than
        40 000 rub. then price for every product equated small price.
        """
        before, after = self.setup_for_before_and_after_test(
            'wholesale_medium', 'wholesale_small'
        )
        self.add_products_to_card(before)
        self.cart.remove(self.second_product)
        total = self.get_remove_total(before, after)
        self.run_remove_test(after, total)

    def test_remove_wholesale_large_to_wholesale_medium(self):
        """
        Test changing price type after remove product from card.

        If the sum of prices on large wholesale is less than
        100 000 rub. then price for every product equated medium price.
        """
        before, after = self.setup_for_before_and_after_test(
            'wholesale_large', 'wholesale_medium'
        )
        self.add_products_to_card(before)
        self.cart.remove(self.second_product)
        total = self.get_remove_total(before, after)
        self.run_remove_test(after, total)

    def test_set_wholesale_small_to_price(self):
        """
        Test changing price type after set product quality in card.

        If the sum of prices on small wholesale is less than
        15 000 rub. then price for every product equated default price.
        """
        before, after = self.setup_for_before_and_after_test(
            'wholesale_small', 'price'
        )
        self.add_products_to_card(before)
        self.cart.set_product_quantity(
            self.second_product, after['second_product_quantity']
        )
        total = self.get_set_total(before, after)
        self.run_remove_test(after, total)

    def test_set_wholesale_medium_to_wholesale_small(self):
        """
        Test changing price type after set product quality in card.

        If the sum of prices on medium wholesale is less than
        40 000 rub. then price for every product equated small price.
        """
        before, after = self.setup_for_before_and_after_test(
            'wholesale_medium', 'wholesale_small'
        )
        self.add_products_to_card(before)
        self.cart.set_product_quantity(
            self.second_product, after['second_product_quantity']
        )
        total = self.get_set_total(before, after)
        self.run_remove_test(after, total)

    def test_set_wholesale_large_to_wholesale_medium(self):
        """
        Test changing price type after set product quality in card.

        If the sum of prices on large wholesale is less than
        40 000 rub. then price for every product equated medium price.
        """
        before, after = self.setup_for_before_and_after_test(
            'wholesale_large', 'wholesale_medium'
        )
        self.add_products_to_card(before)
        self.cart.set_product_quantity(
            self.second_product, after['second_product_quantity']
        )
        total = self.get_set_total(before, after)
        self.run_remove_test(after, total)

    def test_set_price_to_wholesale_small(self):
        """
        Test changing price type after set product quality in card.

        If the sum of prices on small wholesale is less than
        15 000 rub. then price for every product equated default price.
        """
        before, after = self.setup_for_before_and_after_test(
            'price', 'wholesale_small'
        )
        self.add_products_to_card(before)
        self.cart.set_product_quantity(
            self.first_product, after['first_product_quantity']
        )
        self.cart.set_product_quantity(
            self.second_product, after['second_product_quantity']
        )
        total = self.get_add_total(after)
        self.run_add_test(after, total)

    def test_set_wholesale_small_to_wholesale_medium(self):
        """
        Test changing price type after set product quality in card.

        If the sum of prices on medium wholesale is less than
        40 000 rub. then price for every product equated small price.
        """
        before, after = self.setup_for_before_and_after_test(
            'wholesale_small', 'wholesale_medium'
        )
        self.add_products_to_card(before)
        self.cart.set_product_quantity(
            self.first_product, after['first_product_quantity']
        )
        self.cart.set_product_quantity(
            self.second_product, after['second_product_quantity']
        )
        total = self.get_add_total(after)
        self.run_add_test(after, total)

    def test_set_wholesale_medium_to_wholesale_large(self):
        """
        Test changing price type after set product quality in card.

        If the sum of prices on large wholesale is less than
        40 000 rub. then price for every product equated medium price.
        """
        before, after = self.setup_for_before_and_after_test(
            'wholesale_medium', 'wholesale_large'
        )
        self.add_products_to_card(before)
        self.cart.set_product_quantity(
            self.first_product, after['first_product_quantity']
        )
        self.cart.set_product_quantity(
            self.second_product, after['second_product_quantity']
        )
        total = self.get_add_total(after)
        self.run_add_test(after, total)
