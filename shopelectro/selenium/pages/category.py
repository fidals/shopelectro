import typing

from shopelectro.selenium.elements import ProductCard
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

    def product_cards(self) -> typing.List[ProductCard]:
        pass

    def add_to_cart(self, product_cards=None: typing.List[ProductCard]):
        product_cards = product_cards or self.product_cards()[:6]
        for card in product_cards:
            card.add_to_cart()
