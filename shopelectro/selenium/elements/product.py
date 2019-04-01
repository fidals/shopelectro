import abc

from shopelectro.selenium.elements import Button
from shopelectro.selenium.driver import SiteDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Unavailable(NotImplementedError):

    def __init__(self, msg, *args, **kwargs):
        super().__init__(f'The element doesn\'t provide ability to {msg}', *args, **kwargs)


class Product(abc.ABC):
    """"Represent a product at the site."""

    def name(self):
        raise Unavailable('determine the product name.')

    def price(self):
        raise Unavailable('determine the product price.')

    def quantity(self):
        raise Unavailable('determine the product quantity.')

    def add_to_cart(self):
        raise Unavailable('add the product to the card.')

    def remove_from_cart(self):
        raise Unavailable('remove the product from the card.')



class CatalogProduct(Product):
    """"Represent a product card from a catalog."""

    def __init__(self, driver: SiteDriver, card_index: int):
        """
        Ctor.

        :param int card_index: The index number of the product card at a category page
        """
        self.driver = driver
        self.button = Button(
            self.driver,
            (By.XPATH, f'//*[@id="products-wrapper"]/div[{card_index}]/div[2]/div[5]/button')
        )

    def add_to_cart(self):
        self.button.click()


class CartPosition(Product):
    """"Represent a position from cart."""

    def __init__(self, driver: SiteDriver, pos_index: int):
        self.driver = driver
        self.pos_index = pos_index

    def xpath_to(self, path):
        return (By.XPATH, f'//ul[@id="basket-list"]/li[{self.pos_index}]/' + path)

    def name(self):
        raise Unavailable('determine the position name.')

    def price(self):
        raise Unavailable('determine the position price.')

    def quantity(self):
        raise Unavailable('determine the position quantity.')

    def remove_from_cart(self):
        raise Unavailable('remove the position from the card.')
