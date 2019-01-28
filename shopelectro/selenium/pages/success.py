from shopelectro.selenium.pages import Page

from pages.models import CustomPage


class SuccesPage(Page):

    @property
    def path(self):
        CustomPage.objects.get(slug='order-success').url

    def is_success(self):
        return 'Заказ принят' in self.driver.find_element_by_tag_name('h1').text
