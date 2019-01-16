from selenium.driver import SiteDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ProductCard:
    """"Represent a product card from category page."""

    def __init__(self, driver: SiteDriver, card_index: int):
        """
        Ctor.

        :param int card_index: The index number of the product card at a category page
        """
        self.driver = driver
        self.button_xpath = f'//*[@id="products-wrapper"]/div[{card_index}]/div[2]/div[5]/button'

    def add_to_cart(self):
        self.driver.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.button_xpath))
        ).click()
