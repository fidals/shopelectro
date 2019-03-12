from shopelectro.models import PaymentOptions
from shopelectro.selenium.elements import Input, Button
from shopelectro.selenium.pages import Page, matched_url

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.models import CustomPage

# @todo #682:120m Implement and reuse shopelectro.selenium.OrderPage for selenium tests.


class OrderPage(Page):

    def __init__(self, driver):
        super().__init__(driver)
        self.submit_button = Button(self.driver, (By.ID, 'submit-order'))

    @property
    def path(self):
        return CustomPage.objects.get(slug='order').url

    @matched_url
    def fill_contacts(
        self, name='Name', city='Санкт-Петербург', phone='2222222222', email='test@test.test',
    ):
        contacts = {
            'id_name': name,
            'id_city': city,
            'id_phone': phone,
            'id_email': email,
        }

        for id_, value in contacts.items():
            Input(self.driver, (By.ID, id_)).send_keys(value)

    @matched_url
    def make_order(self):
        self.submit_button.click()
        self.driver.wait.until(EC.url_changes(self.path))

    @matched_url
    def select_payment_type(self, payment_option: PaymentOptions):
        if payment_option not in PaymentOptions:
            raise ValueError(
                'An invalid payment type provided.'
                f'It should be one of: {PaymentOptions}'
            )

        item = Button(
            self.driver,
            (By.CSS, f'input[name="payment_type"][value="{payment_option.name}"]'),
        )
        item.click()
