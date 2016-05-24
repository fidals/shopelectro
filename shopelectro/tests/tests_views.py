"""
Tests for shopelectro.ru

There should be test suite for every 'page' on a site,
containing Selenium-based tests.

For running test, you should first run standard Django's development server on port 8000.
        python manage.py runserver
"""
import time

from selenium import webdriver
from django.test import TestCase
from django.conf import settings


class CategoryPageSeleniumTests(TestCase):
    """
    Selenium-based tests for category page UI.
    """

    def setUp(self):
        """Sets up testing urls and dispatches selenium webdriver."""

        self.accumulators_page = settings.LOCALHOST + 'catalog/categories/akkumuliatory/'
        self.supplies_page = settings.LOCALHOST + 'catalog/categories/bloki-pitaniia/'
        self.charger_page = (settings.LOCALHOST +
                             'catalog/categories/zariadnye-ustroistva/')
        self.deep_category = (settings.LOCALHOST +
                              'catalog/categories/akkumuliatory-aa/')
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)

    def tearDown(self):
        """Closes selenium's session."""

        self.browser.quit()

    def test_breadcrumbs(self):
        """
        Breadcrumbs should be presented on every category page.
        Their count depends on category's depth in a catalog tree.
        For the root categories, for example, there should be 3 crumbs.
        :return:
        """

        # In 'root category' there should be three crumbs
        self.browser.get(self.accumulators_page)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 3)

        # In 'deep category' there should be more crumbs
        self.browser.get(self.deep_category)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 4)

    def test_30_products_by_default(self):
        """By default any CategoryPage should contain 30 products."""

        self.browser.get(self.accumulators_page)
        loaded_products = self.browser.find_element_by_class_name('js-products-showed-count').text
        self.assertEqual('30', loaded_products)

    def test_load_more_products(self):
        """
        We can load another 30 by clicking load more button.

        After that we wait some time for XHR will be performed
        and there will be new count of loaded products.
        """

        self.browser.get(self.accumulators_page)
        load_more_button = self.browser.find_element_by_id('btn-load-products')
        load_more_button.click()  # Let's load another 30 products.
        time.sleep(1)  # Dirty hack
        loaded_products = self.browser.find_element_by_class_name(
            'js-products-showed-count').text
        self.assertEqual('60', loaded_products)

    def test_load_more_hidden_if_all_products_were_loaded(self):
        """If all products were loaded we shouldn't see load more button anymore."""

        self.browser.get(self.charger_page)  # There are only 33 of them
        load_more_button = self.browser.find_element_by_id('btn-load-products')
        load_more_button.click()
        time.sleep(1)
        load_more_button = self.browser.find_element_by_id('btn-load-products')
        self.assertTrue('hidden' in load_more_button.get_attribute('class'))

    def test_load_more_not_present_in_fully_loaded_categories(self):
        """If category has <= 30 products, we should not see load more button in its page."""

        # There are only 8 of them, no need of load more
        self.browser.get(self.supplies_page)
        load_more_button = self.browser.find_element_by_id('btn-load-products')
        self.assertTrue('hidden' in load_more_button.get_attribute('class'))

    def test_default_view_is_tile(self):
        """
        By default, category page should has tile view

        It means, after rendering a page, tile view selector should has 'active' class
        and category wrapper 'view-mode-tile' class.
        """

        self.browser.get(self.accumulators_page)
        tile_view_selector = self.browser.find_element_by_class_name('js-icon-mode-tile')
        products_view = self.browser.find_element_by_id('category-right')
        self.assertTrue('active' in tile_view_selector.get_attribute('class'))
        self.assertTrue(
            'view-mode-tile' in products_view.get_attribute('class'))

    def test_change_view(self):
        """
        We should be able to change default view to list view without reloading a page.
        :return:
        """

        self.browser.get(self.accumulators_page)
        list_view_selector = self.browser.find_element_by_class_name('js-icon-mode-list')
        products_view = self.browser.find_element_by_id('category-right')

        self.assertFalse('active' in list_view_selector.get_attribute('class'))
        self.assertFalse('view-mode-list' in products_view.get_attribute('class'))

        list_view_selector.click()
        self.assertTrue('active' in list_view_selector.get_attribute('class'))
        self.assertTrue('view-mode-list' in products_view.get_attribute('class'))

    def test_default_sorting_is_by_cheapest(self):
        """By default, sorting should be by cheapest goods."""

        self.browser.get(self.accumulators_page)
        cheapest_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/div[1]/div/div/div[2]/label/div/select/option[1]')
        self.assertTrue(cheapest_sort_option.is_selected())

    def test_change_sorting(self):
        """We can change sorting option"""
        self.browser.get(self.accumulators_page)
        expensive_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/div[1]/div/div/div[2]/label/div/select/option[3]'
        )
        expensive_sort_option.click()
        expensive_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/div[1]/div/div/div[2]/label/div/select/option[3]'
        )
        self.assertTrue(expensive_sort_option.is_selected())


class ProductPageSeleniumTests(TestCase):
    """
    Selenium-based tests for product page UI.
    """

    def setUp(self):
        """Sets up testing url and dispatches selenium webdriver."""

        self.test_product_page = settings.LOCALHOST + 'catalog/products/3993/'
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)

    def tearDown(self):
        """Closes selenium's session."""

        self.browser.quit()

    def test_breadcrumbs(self):
        """
        Breadcrumbs should be presented on every product page.
        Their count depends on product's depth in a catalog tree.
        :return:
        """

        # There should be 5 items in breadcrumbs for this case
        self.browser.get(self.test_product_page)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 5)

    def test_ui_elements(self):
        """
        Every ProductPage should have buttons to make order and input
        for phone number
        """

        self.browser.get(self.test_product_page)
        button_order = self.browser.find_element_by_id('btn-to-basket')
        button_one_click_order = self.browser.find_element_by_id('btn-one-click-order')
        input_one_click_order = self.browser.find_element_by_id('input-one-click-email')
        self.assertTrue(button_order)
        self.assertTrue(button_one_click_order)
        self.assertTrue(input_one_click_order)

    def test_fancybox(self):
        """ProductPage should have fancyBox plugin"""

        self.browser.get(self.test_product_page)
        product_main_img = self.browser.find_element_by_id('product-image-big')
        product_main_img.click()
        time.sleep(1)
        fancybox_wrap = self.browser.find_element_by_class_name('fancybox-wrap')
        self.assertTrue(fancybox_wrap)

    def test_images_switch(self):
        """If product has > 1 image, we could to switch them by clicking."""

        self.browser.get(self.test_product_page)
        product_main_img = self.browser.find_element_by_id('product-image-big')
        self.assertTrue('main' in product_main_img.get_attribute('src'))

        next_product_img = self.browser.find_element_by_xpath('//*[@id="product-images"]/div[3]')
        next_product_img.click()
        time.sleep(1)
        self.assertFalse('main' in product_main_img.get_attribute('src'))

    def test_one_click_buy_input(self):
        """By default .btn-one-click-order should be disabled"""

        self.browser.get(self.test_product_page)
        input_one_click_order = self.browser.find_element_by_id('input-one-click-email')
        button_one_click_order = self.browser.find_element_by_id('btn-one-click-order')
        input_one_click_order.clear()

        self.assertTrue(button_one_click_order.get_attribute('disabled'))
