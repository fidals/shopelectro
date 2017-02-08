"""
Selenium-based tests.

If you need to create new test-suite, subclass it from SeleniumTestCase class.
Every Selenium-based test suite uses fixture called dump.json.
"""

import time

from selenium import webdriver

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from shopelectro.models import Product


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super(SeleniumTestCase, cls).setUpClass()
        mobile_emulation = {'deviceName': 'Apple iPhone 5'}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)
        cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        cls.browser.implicitly_wait(5)
        cls.browser.maximize_window()

    @classmethod
    def tearDownClass(cls):
        """Close selenium session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()


class Mobile(SeleniumTestCase):

    def setUp(self):
        """Set up testing urls and dispatch selenium webdriver."""
        self.browser.get(self.live_server_url)
        self.toggler = 'js-mobile-menu-toggler'

    def test_ui(self):
        """
        Test mobile ui:
        - off-canvas menu;
        - catalog button;
        - bottom fixed mobile cart;
        - off-canvas menu search input;
        """
        toggler = self.browser.find_element_by_class_name(self.toggler)
        self.assertTrue(toggler.is_displayed())

        catalog = self.browser.find_element_by_class_name('js-mobile-catalog-btn')
        self.assertTrue(catalog.is_displayed())

        cart = self.browser.find_element_by_class_name('js-header-cart')
        self.assertTrue(cart.is_displayed())

        toggler.click()
        search_input = self.browser.find_element_by_class_name('js-search-input')
        self.assertTrue(search_input.is_displayed())

    def test_search(self):
        """Autocomplete in mobile search should work."""
        toggler = self.browser.find_element_by_class_name(self.toggler)
        toggler.click()
        search_input = self.browser.find_element_by_class_name('js-search-input')
        search_input.send_keys('Cate')
        wait()
        autocomplete = self.browser.find_element_by_class_name('autocomplete-suggestions')

        self.assertTrue(autocomplete.is_displayed())

    def test_catalog(self):
        """Catalog should expand on click on fa fa-chevron icons."""
        catalog = self.browser.find_element_by_class_name('js-mobile-catalog-btn')
        catalog.click()
        catalog_item = self.browser.find_element_by_class_name('js-mobile-menu-item')
        wait()
        self.assertTrue(catalog_item.is_displayed())

        catalog_item_icon = self.browser.find_element_by_class_name('js-mobile-link-arrow')
        catalog_item_icon.click()
        catalog_subitem = self.browser.find_element_by_class_name('mobile-catalog-sub-link')
        wait()
        self.assertTrue(catalog_subitem.is_displayed())

    def test_cart(self):
        """Cart should updated after Product buy."""
        product_id = Product.objects.first().id
        product_page = self.live_server_url + reverse('product', args=(product_id,))
        self.browser.get(product_page)

        buy_btn = self.browser.find_element_by_id('btn-to-basket')
        self.browser.execute_script('return arguments[0].scrollIntoView();', buy_btn)

        buy_btn.click()
        wait()
        size = self.browser.find_element_by_class_name('js-cart-size').text
        price = self.browser.find_element_by_class_name('js-mobile-cart-price').text

        self.assertTrue(int(size) > 0)
        self.assertTrue(int(price) > 0)
