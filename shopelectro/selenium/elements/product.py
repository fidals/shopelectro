import abc

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from shopelectro.selenium.elements import Button, Unavailable
from shopelectro.selenium.driver import SiteDriver


class Product(abc.ABC):

    def name(self):
        raise Unavailable('determine the product name.')

    def vendor_code(self):
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

    def __init__(
        self,
        driver: SiteDriver,
        *,
        index: int = None,
        id_: int = None,
    ):
        """
        Ctor.

        :param int index: The index number of the product card at a category page
        """
        self.driver = driver

        if (index is None and not id_) or (index and id_):
            raise ValueError('Provide either index or id_ to work with card.')
        self._id = id_
        self._index = index

    def _build_xpath(self, path=''):
        product_xpath = '//*[@id="products-wrapper"]'

        if self._id:
            return f'{product_xpath}//*[@data-product-id="{self._id}"]/{path}'

        # xpath indexes starts from 1
        return f'{product_xpath}/div[{self._index + 1}]/{path}'

    def vendor_code(self):
        if self._id:
            return self._id
        return self.driver.wait.until(EC.visibility_of_element_located(
            (By.XPATH, self._build_xpath('div[2]/div[1]'))
        )).text.split(' ')[1]

    def add_to_cart(self):
        Button(self.driver, (By.XPATH, self._build_xpath('div[2]/div[5]/button'))).click()


class ProductCard(Product):

    def __init__(self, driver: SiteDriver):
        self.driver = driver

    def add_to_cart(self):
        Button(self.driver, (By.CLASS_NAME, 'js-to-cart-on-product-page')).click()


class CartPosition(Product):

    def __init__(self, driver: SiteDriver, index: int):
        self.driver = driver
        # xpath indexes starts from 1
        self.xpath = f'//ul[@id="basket-list"]/li[{index + 1}]/'

    def __hash__(self):
        el = self._data_element()
        return hash(el.get_attribute('data-product-id') + '/' + el.get_attribute('data-product-count'))

    def __eq__(self, other: 'CartPosition'):
        return hash(self) == hash(other)

    def _data_element(self):
        # use short_wait, because a position could be stale
        return self.driver.short_wait.until(EC.presence_of_element_located(
            (By.XPATH, f'{self.xpath}i')
        ))

    def name(self):
        raise Unavailable('determine the position name.')

    def price(self):
        raise Unavailable('determine the position price.')

    def quantity(self):
        return self._data_element().get_attribute('data-product-count')

    def remove_from_cart(self):
        Button(self.driver, (By.XPATH, f'{self.xpath}i')).click()
