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
        with self.cart().wait_changes():
            elements.ProductCard(self.driver).add_to_cart()
