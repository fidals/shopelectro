import typing

from shopelectro.selenium.pages import Page

from django.urls import reverse

from pages.models import CustomPage

# @todo #682:120m Implement and reuse shopelectro.selenium.OrderPage for selenium tests.


class OrderPage(Page):

    def __init__(self, driver):
        super().__init__(driver)

    @property
    def path(self):
        return CustomPage.objects.get(slug='order').url

    def fill_contacts(self, contacts):
        raise NotImplementedError

    def make_order(self):
        raise NotImplementedError

    def select_payment_type(self):
        raise NotImplementedError
