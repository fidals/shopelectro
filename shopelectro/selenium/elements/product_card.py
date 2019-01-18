from shopelectro.selenium.elements import Button
from shopelectro.selenium.driver import SiteDriver

from selenium.webdriver.common.by import By


class ProductCard:
    """"Represent a product card from category page."""

    def __init__(self, driver: SiteDriver, card_index: int):
        """
        Ctor.

        :param int card_index: The index number of the product card at a category page
        """
        self.driver = driver
        self.button = Button(
            self.driver,
            (By.XPATH, f'//*[@id="products-wrapper"]/div[{card_index}]/div[2]/div[5]/button')
        )

    def add_to_cart(self):
        self.button.click()
