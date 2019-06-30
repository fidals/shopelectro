from django.urls import reverse

from shopelectro.selenium import elements
from shopelectro.selenium.pages import Page


# @todo #682:120m Implement and reuse shopelectro.selenium.Product for selenium tests.


class Product(Page):

    def __init__(self, driver, vendor_code):
        super().__init__(driver)
        self.vendor_code = vendor_code

    @property
    def path(self):
        return reverse('product', args=(self.vendor_code,))

    def add_to_cart(self):
        def wait_adding(browser):
            # @todo #808:60m Create a context manager for cart-related tests.
            #  It should wait position changes after inner block.
            return len(elements.Cart(browser).positions()) > old_count

        old_count = len(self.cart().positions())
        elements.ProductCard(self.driver).add_to_cart()
        self.driver.wait.until(wait_adding)
