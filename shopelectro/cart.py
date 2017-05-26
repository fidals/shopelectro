from collections import OrderedDict
from functools import wraps

from django.db.models import Model

from ecommerce.cart import Cart

from shopelectro.config import PRICE_BOUNDS
from shopelectro.models import Product


class SECartAddError(Exception):
    """Shopelectro cart error."""


def recalculate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        recalculate_price(func(*args, **kwargs))
    return wrapper


def recalculate_price(cart: Cart):
    """
    Define what type of price should be used in Cart. Actualize price if
    needed.
    """
    wholesale_types = OrderedDict([
        ('wholesale_large', PRICE_BOUNDS['wholesale_large']),
        ('wholesale_medium', PRICE_BOUNDS['wholesale_medium']),
        ('wholesale_small', PRICE_BOUNDS['wholesale_small']),
    ])

    product_ids = [position['id'] for _, position in cart]
    products = Product.objects.filter(id__in=product_ids)

    def get_product(id_):
        return next((product for product in products if product.id == id_), {})

    def get_product_data(price_type: str) -> list:
        return [{
            'id': vendor_code,
            'quantity': position['quantity'],
            'price': getattr(
                get_product(position['id']), price_type or 'price',
            ),
        } for vendor_code, position in cart]

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
        If price_type is NoneType, then it is retail price,
        set price from Product.price
        """
        cart.update_product_prices(get_product_data(price_type))

    set_position_prices(define_price_type())


class SECart(Cart):
    """Override Cart class for Wholesale features"""

    def get_product_data(self, product):
        """Add id to position data."""
        return {
            **super().get_product_data(product),
            'id': product.id
        }

    @recalculate
    def add(self, product: Model, quantity=1):
        """
        Replace id to vendor_code as key in cart, because in Order model
        we are save product's id, name, price, quantity and after in email
        templates try reverse urls by order's product id, but should by
        vendor_code.
        """
        required_fields = ['vendor_code', 'name', 'price']
        for field in required_fields:
            has = hasattr(product, field)
            if not has:
                raise SECartAddError(
                    'Product has not required field {}'.format(field))

        if product.vendor_code not in self:
            self._cart[product.vendor_code] = self.get_product_data(product)
            self._cart[product.vendor_code]['quantity'] = quantity
        else:
            self._cart[product.vendor_code]['quantity'] += quantity
        self.save()
        return self

    @recalculate
    def set_product_quantity(self, product, quantity):
        """
        Override set_product_quantity method because it changing state of the
        Cart instance
        """
        super().set_product_quantity(product, quantity)
        return self

    @recalculate
    def remove(self, product):
        """
        Override remove method because it changing state of the Cart instance
        """
        super().remove(product)
        return self
