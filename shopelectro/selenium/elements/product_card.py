from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ProductCard:
    """"Represent a product card of category page."""

    def __init__(self, driver, card_number):
        self.driver = driver
        self.button_xpath = f'//*[@id="products-wrapper"]/div[{card_number}]/div[2]/div[5]/button'

    def _get_element(self, xpath):
        self.driver.wait.until(EC.visibility_of_element_located(By.XPATH, xpath))

    def add_to_cart(self):
        self._get_element(self.xpath).click()

    def set_quantity(self, quantity):
        pass
