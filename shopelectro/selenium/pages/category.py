import typing

from shopelectro.selenium.elements import CatalogProduct
from shopelectro.selenium.pages import Page

from django.urls import reverse

# @todo #682:120m Implement and reuse shopelectro.selenium.CategoryPage for selenium tests.


class CategoryPage(Page):

    def __init__(self, driver, slug):
        super().__init__(driver)
        self.slug = slug

    @property
    def path(self):
        return reverse('category', args=(self.slug,))

    def products(self) -> typing.List[CatalogProduct]:
        raise NotImplementedError

    def add_to_cart(self, products: typing.List[CatalogProduct]=None):
        default = [CatalogProduct(self.driver, i) for i in range(1, 7)]
        products = products or default
        for product in products:
            product.add_to_cart()
