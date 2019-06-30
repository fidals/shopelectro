import abc

from shopelectro.selenium.elements import Button, Unavailable
from shopelectro.selenium.driver import SiteDriver

from selenium.webdriver.common.by import By


class Product(abc.ABC):

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


class CatalogCard(Product):

    def __init__(self, driver: SiteDriver, card_index: int):
        """
        Ctor.

        :param int card_index: The index number of the product card at a category page
        """
        self.driver = driver
        self.xpath = f'//*[@id="products-wrapper"]/div[{card_index}]/div[2]/div[5]/'

    def add_to_cart(self):
        Button(self.driver, (By.XPATH, f'{self.xpath}button')).click()


class ProductCard(Product):

    def __init__(self, driver: SiteDriver):
        self.driver = driver

    def add_to_cart(self):
        Button(self.driver, (By.CLASS_NAME, 'js-to-cart-on-product-page')).click()


class CartPosition(Product):

    def __init__(self, driver: SiteDriver, pos_index: int):
        self.driver = driver
        # xpath indexes starts from 1
        self.xpath = f'//ul[@id="basket-list"]/li[{pos_index + 1}]/'

    def name(self):
        raise Unavailable('determine the position name.')

    def price(self):
        raise Unavailable('determine the position price.')

    def quantity(self):
        raise Unavailable('determine the position quantity.')

    def remove_from_cart(self):
        Button(self.driver, (By.XPATH, f'{self.xpath}i')).click()
