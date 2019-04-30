"""
Selenium-based tests.

If you need to create new test-suite, subclass it from SeleniumTestCase class.
Every Selenium-based test suite uses fixture called dump.json.
"""
import unittest

from django.conf import settings
from django.test import LiveServerTestCase, override_settings, tag
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from shopelectro.selenium import SiteDriver
from shopelectro.models import Category, Product


class MobileSeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']
    host = settings.LIVESERVER_HOST

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super().setUpClass()
        capabilities = {
            'browserName': 'chrome',
            'mobileEmulation': {
                'deviceName': 'Apple iPhone 5',
            },
        }
        cls.browser = SiteDriver(
            site_url=cls.live_server_url,
            desired_capabilities=capabilities,
        )
        cls.browser.set_window_size(400, 800)
        cls.browser.implicitly_wait(10)

    @property
    def wait(self):
        return self.browser.wait

    @classmethod
    def tearDownClass(cls):
        """Close selenium session."""
        cls.browser.quit()
        super().tearDownClass()


@tag('slow')
class Mobile(MobileSeleniumTestCase):

    def setUp(self):
        """Set up testing urls and dispatch selenium webdriver."""
        self.browser.get('/')
        self.wait_page_loading()

    def wait_page_loading(self):
        self.wait.until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, 'content')
            )
        )

    @property
    def search_input(self):
        return self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'js-search-input')
        ))

    def toggle_menu(self):
        self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'js-mobile-menu-toggler')
        )).click()

    def submit_search(self):
        self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'mm-btn')
        )).click()
        self.wait.until(EC.url_contains('/search/'))

    def test_ui(self):
        """
        Test mobile ui.

        - off-canvas menu;
        - catalog button;
        - bottom fixed mobile cart;
        - off-canvas menu search input;
        """
        self.toggle_menu()
        self.assertTrue(self.search_input.is_displayed())

    def test_search_autocomplete(self):
        """Autocomplete in mobile search should work."""
        self.toggle_menu()
        self.search_input.send_keys('Cate')
        suggestions = self.wait.until(EC.visibility_of_any_elements_located(
            (By.CLASS_NAME, 'autocomplete-suggestion')
        ))
        # last autocomplete item has no contains data
        for item in suggestions[:-1]:
            self.assertTrue(item.get_attribute('data-val') == 'Cate')

    def test_search_submit(self):
        """Mobile search form has submit button."""
        self.toggle_menu()
        self.search_input.send_keys('Cate')
        self.submit_search()
        result, *_ = self.wait.until(EC.visibility_of_any_elements_located(
            (By.CLASS_NAME, 'search-result-link')
        ))
        self.assertIn('Cate', result.text)

    def test_catalog(self):
        """Catalog should expand on click on fa fa-chevron icons."""
        catalog = self.browser.find_element_by_class_name('js-mobile-catalog-btn')
        catalog.click()
        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'mobile-catalog-wrapper-list')
        ))
        catalog_item = self.browser.find_element_by_class_name('js-mobile-menu-item')
        self.assertTrue(catalog_item.is_displayed())

        catalog_item_icon = self.browser.find_element_by_class_name('js-mobile-link-arrow')
        catalog_item_icon.click()
        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'mobile-catalog-sub-list')
        ))
        catalog_subitem = self.browser.find_element_by_class_name(
            'mobile-catalog-sub-link'
        )
        self.assertTrue(catalog_subitem.is_displayed())

    # @todo #826:60m Fix mobile selenium driver. STB2
    #  The test shows, that the driver is broken.
    #  Probably we should properly setup desired capabilities of the driver.
    @unittest.expectedFailure
    def test_tags_collapse_state(self):
        """Tags are collapsed by default."""
        self.browser.get(Category.objects.first().url)
        self.wait_page_loading()

        tags = self.browser.wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'js-tags-inputs')
        ))

        self.assertFalse(any(t.is_displayed() for t in tags))

    # CarrotQuest outer js service produces error on this test.
    # Enabled debug makes it off.
    @override_settings(DEBUG=True, INTERNAL_IPS=tuple())
    def test_cart(self):
        """Cart should updated after Product buy."""
        def get_cart_price_and_size():
            size = self.wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'js-cart-size')
            ))
            price = self.wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'js-mobile-cart-price')
            ))
            return price, size

        def wait_updates():
            self.wait.until_not(EC.text_to_be_present_in_element_value(
                (By.CLASS_NAME, 'js-cart-size'), ''
            ))
            self.wait.until_not(EC.text_to_be_present_in_element_value(
                (By.CLASS_NAME, 'js-mobile-cart-price'), ''
            ))

        product_vendor_code = Product.objects.first().vendor_code
        product_page = reverse('product', args=(product_vendor_code,))
        self.browser.get(product_page)
        self.wait_page_loading()

        self.wait.until(EC.visibility_of_element_located(
            (By.ID, 'btn-to-basket')
        )).click()

        wait_updates()
        new_price, new_size = get_cart_price_and_size()

        self.assertEqual(int(new_price.get_attribute('textContent')), 1000)
        self.assertEqual(int(new_size.get_attribute('textContent')), 1)
