"""
Tests for shopelectro.ru

There should be test suite for every 'page' on a site,
containing Selenium-based tests.
"""
import time
from selenium import webdriver
from django.test import TestCase
from django.conf import settings


class CategoryPageSeleniumTests(TestCase):
    """
    Selenium-based tests for category page UI.

    For running them, you should first run standard Django's development server on port 8000.
        python manage.py runserver
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
        loaded_products = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/p/span[1]').text
        self.assertEqual('30', loaded_products)

    def test_load_more_products(self):
        """
        We can load another 30 by clicking load more button.

        After that we wait some time for XHR will be performed
        and there will be new count of loaded products.
        """

        self.browser.get(self.accumulators_page)
        load_more_button = self.browser.find_element_by_xpath(
            '//*[@id="btn-load-products"]')
        load_more_button.click()  # Let's load another 30 products.
        time.sleep(1)  # Dirty hack
        loaded_products = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/p/span[1]').text
        self.assertEqual('60', loaded_products)

    def test_load_more_hidden_if_all_products_were_loaded(self):
        """If all products were loaded we shouldn't see load more button anymore."""

        self.browser.get(self.charger_page)  # There are only 33 of them
        load_more_button = self.browser.find_element_by_xpath(
            '//*[@id="btn-load-products"]')
        load_more_button.click()
        time.sleep(1)
        load_more_button = self.browser.find_element_by_xpath(
            '//*[@id="btn-load-products"]')
        self.assertTrue('hidden' in load_more_button.get_attribute('class'))

    def test_load_more_not_present_in_fully_loaded_categories(self):
        """If category has <= 30 products, we should not see load more button in its page."""

        # There are only 8 of them, no need of load more
        self.browser.get(self.supplies_page)
        load_more_button = self.browser.find_element_by_xpath(
            '//*[@id="btn-load-products"]')
        self.assertTrue('hidden' in load_more_button.get_attribute('class'))

    def test_default_view_is_tile(self):
        """
        By default, category page should has tile view

        It means, after rendering a page, tile view selector should has 'active' class
        and category wrapper 'view-mode-tile' class.
        """

        self.browser.get(self.accumulators_page)
        tile_view_selector = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/div[1]/div/div/div[3]/div[1]')
        products_view = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]')
        self.assertTrue('active' in tile_view_selector.get_attribute('class'))
        self.assertTrue(
            'view-mode-tile' in products_view.get_attribute('class'))

    def test_change_view(self):
        """
        We should be able to change default view to list view without reloading a page.
        :return:
        """

        self.browser.get(self.accumulators_page)
        list_view_selector = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/div[1]/div/div/div[3]/div[2]')
        products_view = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]')

        self.assertFalse('active' in list_view_selector.get_attribute('class'))
        self.assertFalse('view-mode-list' in products_view.get_attribute('class'))

        list_view_selector.click()
        self.assertTrue('active' in list_view_selector.get_attribute('class'))
        self.assertTrue('view-mode-list' in products_view.get_attribute('class'))

    def test_default_sorting_is_by_cheapest(self):
        """By default, sorting should be by cheapest goods."""

        self.browser.get(self.accumulators_page)
        cheapest_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/div[1]/div/div/div[2]/label/select/option[1]')
        self.assertTrue(cheapest_sort_option.is_selected())

    def test_change_sorting(self):
        """We can change sorting option"""
        self.browser.get(self.accumulators_page)
        expensive_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/div[1]/div/div/div[2]/label/select/option[2]'
        )
        expensive_sort_option.click()
        expensive_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/div[1]/div/div/div[2]/label/select/option[2]'
        )
        self.assertTrue(expensive_sort_option.is_selected())
