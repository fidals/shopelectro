from shopelectro.selenium.elements import Input
from shopelectro.selenium.pages import Page

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.models import CustomPage

# @todo #682:120m Implement and reuse shopelectro.selenium.OrderPage for selenium tests.


class OrderPage(Page):

    def __init__(self, driver):
        super().__init__(driver)

    @property
    def path(self):
        return CustomPage.objects.get(slug='order').url

    def fill_contacts(self, contacts=None):
        contacts = contacts or {
            'id_name': 'Name',
            'id_city': 'Санкт-Петербург',
            'id_phone': '2222222222',
            'id_email': 'test@test.test'
        }

        for id_, value in contacts.items():
            Input(self.driver, (By.ID, id_)).send_keys(value)

    def make_order(self):
        self.driver.wait.until(EC.element_to_be_clickable(
            (By.ID, 'submit-order')
        )).click()

    def select_payment_type(self):
        raise NotImplementedError
