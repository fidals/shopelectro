from shopelectro.selenium.elements import Unavailable

# @todo #799:120m Reuse shopelectro.selenium.elements.cart.Cart for selenium tests.


class Cart:
    """"Represent the cart at the site."""

    def __init__(self, driver: SiteDriver):
        self.driver = driver

    def positions(self):
        raise Unavailable('get positions from cart.')

    def clear(self):
        raise Unavailable('clear cart.')

    def total(self):
        raise Unavailable('get total count of positions from cart.')

    def is_empty(self):
        raise Unavailable('determine emptiness of cart.')
