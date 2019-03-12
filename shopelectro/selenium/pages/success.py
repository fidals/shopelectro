from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from shopelectro.selenium.pages import Page, matched_url

from pages.models import CustomPage


class SuccessPage(Page):

    @property
    def path(self):
        return CustomPage.objects.get(slug='order-success').url

    @matched_url
    def is_success(self):
        h1 = self.driver.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, 'h1'))
        ).text
        return 'Заказ принят' in h1
