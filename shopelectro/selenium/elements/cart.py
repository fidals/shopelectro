from contextlib import contextmanager

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from shopelectro.selenium import SiteDriver, elements

# @todo #799:120m Reuse shopelectro.selenium.elements.cart.Cart for selenium tests.


class Cart:
    """"Represent the cart at the site."""

    def __init__(self, driver: SiteDriver):
        self.driver = driver
        self.positions = elements.Positions(
            driver,
            elements.CartPosition,
            (By.CLASS_NAME, 'basket-item'),
        )

    def _hover(self):
        cart = self.driver.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'basket-parent')
        ))
        ActionChains(self.driver).move_to_element(cart).perform()
        self.driver.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'js-cart-wrapper')
        ))

    def remove(self, position: elements.CartPosition):
        with self.positions.wait_changes():
            self._hover()
            position.remove()

    def clear(self):
        self._hover()
        elements.Button(self.driver, (By.CLASS_NAME, 'js-reset-cart')).click()
        self.driver.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'js-cart-is-empty')
        ))

    def total(self):
        raise elements.Unavailable('get total count of positions from cart.')

    def is_empty(self):
        raise elements.Unavailable('determine emptiness of cart.')
