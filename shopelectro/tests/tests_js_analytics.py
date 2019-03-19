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


@tag('slow')
@helpers.disable_celery
@override_settings(DEBUG=True, INTERNAL_IPS=tuple())
class YandexMetrika(helpers.SeleniumTestCase):

    CART_LOCATOR = (By.CLASS_NAME, 'js-go-to-cart')

    def setUp(self):
        product_vendor_code = Product.objects.first().vendor_code
        self.product_page = reverse('product', args=(product_vendor_code,))
        self.category_page = reverse(
            'category', args=(Category.objects.first().page.slug,))
        self.order_page_url = reverse(CustomPage.ROUTE, args=('order',))
        self.browser.get('/')
        wait_page_loading(self.browser)

    @property
    def reached_goals(self):
        """Return yaCounter.goals array after triggering goal."""
        return self.browser.execute_script('return yaCounter20644114.goals;')

    def prevent_default(self, event, selector):
        """Use event.preventDefault() to prevent web page reloading."""
        self.browser.execute_script(
            'var target = document.querySelector("' + selector + '");'
            'console.log(target);'
            'target.on' + event + ' = function(event) {'
            'event.preventDefault();'
            'return false;};'
        )

    def select_text(self, class_name):
        """Programmatically select text on page."""
        self.browser.execute_script(
            'var target = document.getElementsByClassName("' + class_name + '")[0];'
            'var range = document.createRange();'
            'var selection = window.getSelection();'
            'range.selectNode(target);'
            'selection.removeAllRanges();'
            'selection.addRange(range);'
        )

    def buy_product(self):
        self.browser.get(self.product_page)
        wait_page_loading(self.browser)
        self.click((By.ID, 'btn-to-basket'))
        self.wait.until_not(EC.text_to_be_present_in_element(
            (By.CLASS_NAME, 'js-mobile-cart-price'), '0'
        ))

    def go_to_cart(self):
        self.click(self.CART_LOCATOR)
        self.wait.until(EC.url_contains(self.order_page_url))

    def test_download_header_price(self):
        """User clicks Download price button in site's header."""
        self.browser.find_element_by_class_name('js-download-price').click()
        self.assertTrue('PRICE_HEADER' in self.reached_goals)

    def test_download_footer_price(self):
        """User clicks Download price button in site's footer."""
        self.browser.find_element_by_class_name('js-download-price-footer').click()
        self.assertTrue('PRICE_FOOTER' in self.reached_goals)

    def test_backcall_open(self):
        """User clicks Backcall button."""
        self.browser.find_element_by_class_name('js-backcall-order').click()
        self.assertTrue('BACK_CALL_OPEN' in self.reached_goals)

    def test_browse_product_goal_on_index_page(self):
        """User browses to product's page from Index page."""
        self.prevent_default('click', '.js-browse-product')
        self.click((By.CLASS_NAME, 'js-browse-product'))

        self.assertTrue('PROD_BROWSE' in self.reached_goals)

    def test_add_product_from_product_page(self):
        """User adds Product to Cart on Product's page."""
        self.buy_product()

        self.assertTrue('PUT_IN_CART_FROM_PRODUCT' in self.reached_goals)
        self.assertTrue('CMN_PUT_IN_CART' in self.reached_goals)

    def test_add_product_from_category_page(self):
        """"User adds Product to Cart on Category's page."""
        self.browser.get(self.category_page)
        self.browser.find_element_by_class_name('js-product-to-cart').click()

        self.assertTrue('PUT_IN_CART_FROM_CATEGORY' in self.reached_goals)
        self.assertTrue('CMN_PUT_IN_CART' in self.reached_goals)

    def test_delete_from_dropdown(self):
        """User removes Product from Cart dropdown."""
        self.browser.get(self.product_page)
        self.buy_product()
        removed_el = self.click((By.CLASS_NAME, 'js-cart-remove'))
        with self.screen_fail('test_delete_from_dropdown'):
            self.wait.until(EC.staleness_of(removed_el))

        self.assertTrue('DELETE_PRODUCT' in self.reached_goals)

    def test_delete_from_cart_page(self):
        """User removes Product from Cart."""
        self.browser.get(self.product_page)
        self.buy_product()
        self.go_to_cart()
        self.browser.find_element_by_class_name('js-remove').click()

        self.assertTrue('DELETE_PRODUCT' in self.reached_goals)

    def test_use_search(self):
        """User uses search field."""
        self.prevent_default('submit', '.js-search-form')
        self.browser.find_element_by_class_name('js-search-form').submit()

        self.assertTrue('USE_SEARCH_FORM' in self.reached_goals)

    def test_backcall_request(self):
        """Test goal when user requested backcall successfully."""
        make_backcall(self.browser)

        self.assertTrue('BACK_CALL_SEND' in self.reached_goals)

    def test_full_buy_goal(self):
        """User successfully made full Order."""
        submit_button_id = 'submit-order'
        self.buy_product()
        self.go_to_cart()
        self.prevent_default('submit', '#order-form-full')
        self.browser.find_element_by_id('id_phone').send_keys('22222222222')
        self.browser.find_element_by_id('id_email').send_keys('test@test.ru')
        self.browser.find_element_by_id(submit_button_id).click()
        self.wait.until_not(EC.element_to_be_clickable(
            (By.ID, submit_button_id)
        ))

        self.assertTrue('FULL_BUY_SEND' in self.reached_goals)
        self.assertTrue('CMN_BUY_SEND' in self.reached_goals)

    # @todo #718:30m Resurrect `test_cart_page_open` test.
    @unittest.skip
    def test_cart_page_open(self):
        self.buy_product()
        self.prevent_default('click', '.js-go-to-cart')
        self.click(self.CART_LOCATOR)
        self.wait_page_loaded()
        self.assertTrue('CART_OPEN' in self.reached_goals)

        self.prevent_default('click', '.btn-to-order')
        show_cart_dropdown(self.browser)
        self.click((By.CLASS_NAME, 'btn-to-order'))
        self.wait_page_loaded()
        self.assertTrue('CART_OPEN' in self.reached_goals)
