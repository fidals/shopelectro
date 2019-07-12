import abc

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from shopelectro.selenium.elements import Button, Unavailable
from shopelectro.selenium.driver import SiteDriver


class Product(abc.ABC):

    def name(self):
        raise Unavailable('determine the product name.')

    def vendor_code(self):
        raise Unavailable('determine the vendor code.')

    def price(self):
        raise Unavailable('determine the product price.')

    def quantity(self):
        raise Unavailable('determine the product quantity.')

    def add(self):
        raise Unavailable('add the product to the card.')

    def remove(self):
        raise Unavailable('remove the product from the card.')

    def __hash__(self):
        raise NotImplementedError('Provide __hash__ implementation for the class.')

    def __eq__(self, other: 'Product'):
        return hash(self) == hash(other)


class CatalogCard(Product):

    def __init__(
        self,
        driver: SiteDriver,
        *,
        _index: int = None,
        _id: int = None,
    ):
        """
        Ctor.

        :param int _index: The index number of the product card at a category page
        """
        self.driver = driver

        if (_index is None and not _id) or (_index and _id):
            raise ValueError('Provide either _index or _id to work with card.')
        self._id = _id
        self._index = _index

    @classmethod
    def with_id(
        cls,
        driver: SiteDriver,
        id_: int,
    ):
        return cls(driver, _id=id_)

    @classmethod
    def with_index(
        cls,
        driver: SiteDriver,
        index: int,
    ):
        return cls(driver, _index=index)

    def _build_xpath(self, path=''):
        product_xpath = '//*[@id="products-wrapper"]'

        if self._id:
            return f'{product_xpath}//*[@data-product-id="{self._id}"]/{path}'

        # xpath indexes starts from 1
        return f'{product_xpath}/div[{self._index + 1}]/{path}'

    def vendor_code(self):
        return self.driver.wait.until(EC.visibility_of_element_located(
            (By.XPATH, self._build_xpath('div[2]/div[1]'))
        )).text.split(' ')[1]

    def add(self):
        Button(self.driver, (By.XPATH, self._build_xpath('div[2]/div[5]/button'))).click()


class ProductCard(Product):

    def __init__(self, driver: SiteDriver):
        self.driver = driver

    def add(self):
        Button(self.driver, (By.CLASS_NAME, 'js-to-cart-on-product-page')).click()


class CartPosition(Product):

    def __init__(self, driver: SiteDriver, index: int):
        self.driver = driver
        # xpath indexes starts from 1
        self.xpath = f'//ul[@id="basket-list"]/li[{index + 1}]/'

    def __hash__(self):
        el = self._data_element()
        return hash(
            el.get_attribute('data-product-id')
            + '/'
            + el.get_attribute('data-product-count')
        )

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

    def remove(self):
        Button(self.driver, (By.XPATH, f'{self.xpath}i')).click()


class OrderPosition(Product):
    """Represent a product position on order page."""

    def __init__(self, driver: SiteDriver, index: int):
        self.driver = driver
        # xpath indexes starts from 1
        self.xpath = f'//div[@id="js-order-list"]/div[2]/div[{index + 1}]/'

    def __hash__(self):
        return hash(
            self.vendor_code()
            + '/'
            + self.quantity()
        )

    def vendor_code(self):
        return self.driver.short_wait.until(EC.visibility_of_element_located(
            (By.XPATH, f'{self.xpath}div[1]')
        )).text

    def quantity(self):
        return self.driver.short_wait.until(EC.visibility_of_element_located(
            (By.XPATH, f'{self.xpath}//input')
        )).value

    def set(self, quantity: int):
        raise NotImplementedError

    def increase(self, times=1):
        raise NotImplementedError

    def decrease(self, times=1):
        raise NotImplementedError

    def remove(self):
        Button(self.driver, (By.XPATH, f'{self.xpath}div[6]/div')).click()
