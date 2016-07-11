from collections import OrderedDict
from ecommerce.cart import Cart


def recalculate_price(cart: Cart) -> Cart:
    """
    Function defines what type of price should use in cart and if need changes this
    price to the actual.
    """

    wholesale_types = OrderedDict(sorted({
        "wholesale_large": 100000,
        "wholesale_medium": 40000,
        "wholesale_small": 15000,
    }.items(), key=lambda type: type[1], reverse=True))

    def get_product_data(price_type: str) -> list:
        return [{
            'id': str(product['product'].id),
            'price': float(getattr(product['product'], price_type or 'price')),
            'quantity': int(product['quantity'])
        } for product in cart]

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

    def set_items_price(price_type: str) -> Cart:
        """
        If price_type is NoneType, then it is retail price, set price from
        Product.price.
        """
        new_data = get_product_data(price_type)
        return cart.update_product_price(new_data)

    set_items_price(define_price_type())
