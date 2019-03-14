from django.test import override_settings, tag

from shopelectro import selenium
from shopelectro.tests import helpers
from shopelectro.models import CategoryPage, Order


@tag('slow')
@helpers.disable_celery
@override_settings(DEBUG=True, INTERNAL_IPS=tuple())
class GoogleEcommerce(helpers.SeleniumTestCase):

    fixtures = ['dump.json']

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
        success_page.wait_loaded()
        self.assertTrue(success_page.is_success())

        order = Order.objects.order_by('-created').first()  # Ignore PyFlakesBear
        reached = self.browser.execute_script('return gaObject.results;')  # Ignore PyFlakesBear

        # @todo #762:30m Match an order with a transaction of Google eCommerce analytics.
        #  The transaction must contain correct order data and related products.
