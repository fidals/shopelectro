import typing

from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from shopelectro.selenium import elements
from shopelectro.selenium.pages import Page

# @todo #682:120m Implement and reuse shopelectro.selenium.CategoryPage for selenium tests.


class CategoryPage(Page):

    def __init__(self, driver, slug):
        super().__init__(driver)
        self.slug = slug

    @property
    def path(self):
        return reverse('category', args=(self.slug,))

    def product_cards(self) -> typing.List[elements.CatalogCard]:
        products_count = len(self.driver.find_elements(
            By.CLASS_NAME, 'product-card'
        ))
        return [elements.CatalogCard.with_index(self.driver, i) for i in range(products_count)]

    def find_card(self, id_: int) -> elements.CatalogCard:
        return elements.CatalogCard.with_id(self.driver, id_)

    def load_more(self):
        old_len = len(self.product_cards())
        locator = (By.ID, 'btn-load-products')

        if not self.driver.wait.until(EC.presence_of_element_located(
            locator
        )).is_displayed():
            raise elements.Unavailable('load more')

        elements.Button(self.driver, locator).click()

        self.wait.until_not(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'js-products-showed-count'),
                str(old_len),
            )
        )

    def add_to_cart(self, products: typing.List[elements.CatalogCard] = None):
        default = [elements.CatalogCard.with_index(self.driver, i) for i in range(6)]
        products = products or default

        with self.cart().positions.wait_changes():
            for product in products:
                product.add()
