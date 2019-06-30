import typing

from shopelectro.selenium.elements import CatalogCard
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

    def product_cards(self) -> typing.List[CatalogCard]:
        raise NotImplementedError

    def add_to_cart(self, products: typing.List[CatalogCard] = None):
        default = [CatalogCard(self.driver, i) for i in range(1, 7)]
        products = products or default
        for product in products:
            product.add_to_cart()
