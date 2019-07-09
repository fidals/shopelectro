from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.models import CustomPage
from shopelectro.models import PaymentOptions
from shopelectro.selenium import elements, SiteDriver
from shopelectro.selenium.pages import Page

# @todo #682:120m Implement and reuse shopelectro.selenium.OrderPage for selenium tests.


class OrderPage(Page):

    def __init__(self, driver: SiteDriver):
        super().__init__(driver)
        self.submit_button = elements.Button(self.driver, (By.ID, 'submit-order'))
        self.positions = elements.Positions(
            driver,
            elements.OrderPosition,
            (By.XPATH, '//div[@id="js-order-list"]/div[2]/div'),
        )

    @property
    def path(self):
        return CustomPage.objects.get(slug='order').url

    def set(self, position: elements.OrderPosition, quantity: int):
        with self.positions.wait_changes():
            position.set(quantity)

    def increase(self, position: elements.OrderPosition):
        with self.positions.wait_changes():
            position.increase()

    def decrease(self, position: elements.OrderPosition):
        with self.positions.wait_changes():
            position.decrease()

    def remove(self, position: elements.OrderPosition):
        with self.positions.wait_changes():
            position.remove()

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
            elements.Input(self.driver, (By.ID, id_)).send_keys(value)

    def make_order(self):
        self.submit_button.click()
        self.driver.wait.until(EC.url_changes(self.path))

    def select_payment_type(self, payment_option: PaymentOptions):
        if payment_option not in PaymentOptions:
            raise ValueError(
                'An invalid payment type provided.'
                f'It should be one of: {PaymentOptions}'
            )

        item = elements.Button(
            self.driver,
            (By.CSS, f'input[name="payment_type"][value="{payment_option.name}"]'),
        )
        item.click()
