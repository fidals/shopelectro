import typing

from shopelectro.selenium.pages import Page

from django.urls import reverse

from pages.models import CustomPage

# @todo #682:60m Implement and reuse shopelectro.selenium.OrderPage for selenium tests.


class OrderPage(Page):

    def __init__(self, driver):
        super().__init__(driver)

    @property
    def address(self):
        return CustomPage.objects.get(slug='order').url

    def fill_contacts(self, contacts):
        pass

    def make_order(self):
        pass
