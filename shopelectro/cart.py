from collections import OrderedDict
from functools import wraps

from ecommerce.cart import Cart

from shopelectro.config import PRICE_BOUNDS
from shopelectro.models import Product


def recalculate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        recalculate_price(func(*args, **kwargs))
    return wrapper


def recalculate_price(cart: Cart) -> Cart:
    """Define what type of price should be used in Cart. Actualize price if needed."""
    wholesale_types = OrderedDict([
        ('wholesale_large', PRICE_BOUNDS['wholesale_large']),
        ('wholesale_medium', PRICE_BOUNDS['wholesale_medium']),
        ('wholesale_small', PRICE_BOUNDS['wholesale_small']),
    ])

    def get_product_data(price_type: str) -> list:
        product_ids = [id_ for id_, _ in cart]
        products = Product.objects.filter(id__in=product_ids)
        return [{
            'id': id_,
            'price': getattr(products.get(id=id_), price_type or 'price'),
            'quantity': position['quantity']
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
        is_applicable = (lambda price_type:
                         wholesale_types[price_type] <
                         total_wholesale_prices[price_type])

        for price_type in wholesale_types:
            if is_applicable(price_type):
                return price_type

    def set_position_prices(price_type: str):
        """
        If price_type is NoneType, then it is retail price, set price from Product.price"""
        new_data = get_product_data(price_type)
        cart.update_product_prices(new_data)

    set_position_prices(define_price_type())


class SECart(Cart):
    """Override Cart class for Wholesale features"""

    def get_product_data(self, product):
        return {
            **super().get_product_data(product),
            'vendor_code': product.vendor_code
        }

    @recalculate
    def add(self, product, quantity=1):
        """Override add method because it changing state of the Cart instance"""
        super().add(product, quantity)
        return self

    @recalculate
    def set_product_quantity(self, product, quantity):
        """Override set_product_quantity method because it changing state of the Cart instance"""
        super().set_product_quantity(product, quantity)
        return self

    @recalculate
    def remove(self, product):
        """Override remove method because it changing state of the Cart instance"""
        super().remove(product)
        return self
