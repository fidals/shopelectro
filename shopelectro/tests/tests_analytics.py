from django.test import override_settings, tag

from shopelectro import selenium
from shopelectro.models import CategoryPage, Order
from shopelectro.tests.helpers import SeleniumTestCase


@tag('slow')
@override_settings(DEBUG=True, INTERNAL_IPS=tuple())
class GoogleEcommerce(SeleniumTestCase):

    fixtures = ['dump.json']

    order: Order

    def test_google_ecommerce_purchase(self):
        category_page = selenium.CategoryPage(
            self.browser,
            CategoryPage.objects.first().slug,
        )
        category_page.load()
        category_page.add_to_cart()

        order_page = selenium.OrderPage(self.browser)
        order_page.load()
        order_page.fill_contacts()
        order_page.make_order()

        success_page = selenium.SuccessPage(self.browser)
        self.assertTrue(success_page.is_success())

        order = Order.objects.order_by('-created').first()
        reached = self.browser.execute_script('return gaObject.results;')

        # @todo #762:30m Implement assertion of an order and reached targets for test_google_ecommerce_purchase.
