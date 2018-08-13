from collections import OrderedDict
from functools import wraps

from django.db.models import Model
from django.conf import settings

from ecommerce.cart import Cart

from shopelectro.models import Product


def recalculate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        recalculate_price(func(*args, **kwargs))
    return wrapper


def recalculate_price(cart: Cart):
    """
    Define what type of price should be used in Cart.

    Actualize price if needed.
    """
    wholesale_types = OrderedDict([
        ('wholesale_large', settings.PRICE_BOUNDS['wholesale_large']),
        ('wholesale_medium', settings.PRICE_BOUNDS['wholesale_medium']),
        ('wholesale_small', settings.PRICE_BOUNDS['wholesale_small']),
    ])

    product_ids = [id_ for id_, _ in cart]
    products = Product.objects.filter(id__in=product_ids)

    def get_product(id_):
        return next((product for product in products if product.id == id_), {})

    def get_product_data(price_type: str) -> list:
        return [{
            'id': id_,
            'quantity': position['quantity'],
            'price': getattr(
                get_product(id_), price_type or 'price',
            ),
        } for id_, position in cart]

    def get_total_price(price_type: str):
        return sum(
            product_data['price'] * product_data['quantity']
            for product_data in get_product_data(price_type)
        )

    total_wholesale_prices = {
        price_type: get_total_price(price_type)
        for price_type in wholesale_types
    }

    def define_price_type() -> "Wholesale price type" or None:
        def is_applicable(price_type):
            return (
                wholesale_types[price_type] <
                total_wholesale_prices[price_type]
            )

        for price_type in wholesale_types:
            if is_applicable(price_type):
                return price_type

    def set_position_prices(price_type: str):
        """
        Set price from Product.price.

        If price_type is NoneType, then it is retail price, set price from
        Product.price.
        """
        cart.update_product_prices(get_product_data(price_type))

    set_position_prices(define_price_type())


class SECart(Cart):
    """Override Cart class for Wholesale features."""

    def get_product_data(self, product):
        """Add vendor_code to cart's positions data."""
        return {
            **super().get_product_data(product),
            'vendor_code': product.vendor_code
        }

    @recalculate
    def add(self, product: Model, quantity=1):
        super().add(product, quantity)
        return self

    @recalculate
    def set_product_quantity(self, product: Model, quantity: int):
        super().set_product_quantity(product, quantity)
        return self

    @recalculate
    def remove(self, product: Model):
        super().remove(product)
        return self
