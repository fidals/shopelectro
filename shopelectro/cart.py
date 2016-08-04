from collections import OrderedDict
from functools import wraps

from shopelectro.models import Product
from ecommerce.cart import Cart


def recalculate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        recalculate_price(func(*args, **kwargs))
    return wrapper


def recalculate_price(cart: Cart) -> Cart:
    """Define what type of price should be used in cart. Actualize price if needed."""
    wholesale_types = OrderedDict(sorted({
        'wholesale_large': 100000,
        'wholesale_medium': 40000,
        'wholesale_small': 15000,
    }.items(), key=lambda type: type[1], reverse=True))

    def get_product_data(price_type: str) -> list:
        product_ids = [item[0] for item in cart]
        products = Product.objects.filter(id__in=product_ids)
        return [{
            'id': id_,
            'price': getattr(products.get(id=id_), price_type or 'price'),
            'quantity': position['quantity']
        } for id_, position in cart]

    get_total_price_for_product = (lambda product:
                                   product['price'] * product['quantity'])

    total_wholesale_prices = {
        wholesale_price_type: sum(
            get_total_price_for_product(product)
            for product in get_product_data(wholesale_price_type)
        )
        for wholesale_price_type in wholesale_types
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


class WholesaleCart(Cart):
    """Override Cart class for Wholesale features"""
    @recalculate
    def add(self, product, quantity=1):
        """Override add method because it changing state of the Cart instance"""
        super(WholesaleCart, self).add(product, quantity)
        return self

    @recalculate
    def set_product_quantity(self, product, quantity):
        """Override set_product_quantity method because it changing state of the Cart instance"""
        super(WholesaleCart, self).set_product_quantity(product, quantity)
        return self

    @recalculate
    def remove(self, product):
        """Override remove method because it changing state of the Cart instance"""
        super(WholesaleCart, self).remove(product)
        return self
