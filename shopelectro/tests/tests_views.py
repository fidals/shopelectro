"""
Selenium based tests.

There should be test suite for every 'page' on a site.

For running such tests, you should first run Django's development server on port 8000
        python manage.py runserver
"""
import os
import time
from xml.etree import ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from seleniumrequests import Chrome

from django.core.management import call_command
from django.test import TestCase
from django.conf import settings

from catalog.models import Product


def hover(browser, element):
    """Perform a hover over an element."""
    hover_action = ActionChains(browser).move_to_element(element)
    hover_action.perform()


class CategoryPageSeleniumTests(TestCase):
    """
    Selenium-based tests for category page UI.
    """


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)

success_order_page = settings.LOCALHOST + 'shop/success-order/'


class Header(TestCase):
    """Selenium-based tests for header."""

    def setUp(self):
        """Sets up testing urls and dispatches selenium webdriver."""
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
        self.browser.get(settings.LOCALHOST)
        self.call_button = self.browser.find_element_by_class_name(
            'feedback-but-btn')

    def tearDown(self):
        """Closes selenium's session."""
        self.browser.quit()

    def test_call_modal_not_visible(self):
        """By default we shouldn't see call modal."""
        """After clicking on call button we should see call modal."""
        modal = self.browser.find_element_by_id('back-call-modal')
        self.assertFalse(modal.is_displayed())

    def test_call_modal_after_click_call_button(self):
        """After clicking on call button we should see call modal."""
        self.call_button.click()
        wait()
        modal = self.browser.find_element_by_id('back-call-modal')
        self.assertTrue(modal.is_displayed())

    def test_order_call(self):
        """After filling modal's fields we can successfully order call."""
        self.call_button.click()
        wait(3)
        self.browser.find_element_by_id(
            'back-call-phone').send_keys('22222222222')
        day_time = self.browser.find_element_by_xpath(
            '//*[@id="back-call-time"]/option[3]')
        day_time.click()
        self.browser.find_element_by_class_name('js-send-backcall').click()
        wait()
        self.assertTrue(self.browser.find_element_by_class_name(
            'js-backcall-success').is_displayed())

    def test_empty_cart(self):
        """By default there should be 'Корзина пуста' in the header's cart."""
        cart_in_header = self.browser.find_element_by_class_name(
            'js-header-cart')
        self.assertTrue('Корзина пуста' in cart_in_header.text)

    def test_cart_hover(self):
        """When hover, cart dropdown should be visible."""
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        hover(self.browser, cart_parent)
        cart = self.browser.find_element_by_class_name('basket-wrapper')
        self.assertTrue(cart.is_displayed())


class CategoryPage(TestCase):
    """Selenium-based tests for category page UI."""

    def setUp(self):
        """Sets up testing urls and dispatches selenium webdriver."""

        self.accumulators_page = settings.LOCALHOST + 'catalog/categories/akkumuliatory/'
        self.converters_page = settings.LOCALHOST + 'catalog/categories/avtopreobrazovateli-napriazheniia/'
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
        loaded_products = self.browser.find_element_by_class_name(
            'js-products-showed-count').text
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
        wait()
        loaded_products = self.browser.find_element_by_class_name(
            'js-products-showed-count').text
        self.assertEqual('60', loaded_products)

    def test_load_more_hidden_if_all_products_were_loaded(self):
        """If all products were loaded we shouldn't see load more button anymore."""

        self.browser.get(self.converters_page)  # There are only 34 of them
        load_more_button = self.browser.find_element_by_id('btn-load-products')
        load_more_button.click()
        wait()
        load_more_button = self.browser.find_element_by_id('btn-load-products')
        self.assertTrue('hidden' in load_more_button.get_attribute('class'))

    def test_default_view_is_tile(self):
        """
        By default, category page should has tile view

        It means, after rendering a page, tile view selector should has 'active' class
        and category wrapper 'view-mode-tile' class.
        """

        self.browser.get(self.accumulators_page)
        tile_view_selector = self.browser.find_element_by_class_name(
            'js-icon-mode-tile')
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
        list_view_selector = self.browser.find_element_by_class_name(
            'js-icon-mode-list')
        products_view = self.browser.find_element_by_id('category-right')

        self.assertFalse('active' in list_view_selector.get_attribute('class'))
        self.assertFalse(
            'view-mode-list' in products_view.get_attribute('class'))

        list_view_selector.click()
        self.assertTrue('active' in list_view_selector.get_attribute('class'))
        self.assertTrue(
            'view-mode-list' in products_view.get_attribute('class'))

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

    def test_add_to_cart(self):
        """We can add item to cart from it's category page."""
        self.browser.get(self.charger_page)
        self.browser.find_elements_by_class_name(
            ' js-product-to-cart')[0].click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name(
            'js-cart-is-empty')
        self.assertFalse(cart_is_empty.is_displayed())


class ProductPage(TestCase):
    """
    Selenium-based tests for product page UI.
    """

    def setUp(self):
        """Sets up testing url and dispatches selenium webdriver."""

        self.test_product_page = settings.LOCALHOST + 'catalog/products/3993/'
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
        self.browser.get(self.test_product_page)
        self.one_click = self.browser.find_element_by_id('btn-one-click-order')

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
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 5)

    def test_ui_elements(self):
        """
        Every ProductPage should have buttons to make order and input
        for phone number
        """
        button_order = self.browser.find_element_by_id('btn-to-basket')
        input_one_click_order = self.browser.find_element_by_id(
            'input-one-click-phone')
        self.assertTrue(button_order)
        self.assertTrue(self.one_click)
        self.assertTrue(input_one_click_order)

    def test_fancybox(self):
        """ProductPage should have fancyBox plugin"""
        product_main_img = self.browser.find_element_by_id('product-image-big')
        product_main_img.click()
        wait()
        fancybox_wrap = self.browser.find_element_by_class_name(
            'fancybox-wrap')
        self.assertTrue(fancybox_wrap)

    def test_images_switch(self):
        """If product has > 1 image, we could to switch them by clicking."""
        product_main_img = self.browser.find_element_by_id('product-image-big')
        self.assertTrue('main' in product_main_img.get_attribute('src'))

        next_product_img = self.browser.find_element_by_xpath(
            '//*[@id="product-images"]/div[2]/img')
        next_product_img.click()
        wait()
        self.assertFalse('main' in product_main_img.get_attribute('src'))

    def test_one_click_buy_disabled_with_empty_phone(self):
        """By default .btn-one-click-order should be disabled"""
        self.browser.find_element_by_id('input-one-click-phone').clear()
        self.assertTrue(self.one_click.get_attribute('disabled'))

    def test_one_click_buy_active_with_phone_filled(self):
        """.btn-one-click-order should be active if phone is filled."""
        self.browser.find_element_by_id(
            'input-one-click-phone').send_keys('22222222222')
        self.assertFalse(self.one_click.get_attribute('disabled'))

    def test_one_click_buy_action(self):
        """We can order product via one-click buy button."""
        self.browser.find_element_by_id(
            'input-one-click-phone').send_keys('22222222222')
        self.one_click.click()
        wait()
        self.assertEqual(self.browser.current_url, success_order_page)

    def test_add_to_cart(self):
        """We can add item to cart from it's page."""
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name(
            'js-cart-is-empty')
        self.assertFalse(cart_is_empty.is_displayed())

    def test_product_name_in_cart_dropdown(self):
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        hover(self.browser, cart_parent)
        cart = self.browser.find_element_by_class_name('basket-wrapper')
        self.assertTrue('Аккумулятор Panasonic' in cart.text)

    def test_actual_product_count_in_cart_dropdown(self):
        self.browser.find_element_by_id('product-count').send_keys('42')
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        hover(self.browser, cart_parent)
        cart_size = self.browser.find_element_by_class_name('js-cart-size')
        self.assertTrue('42' in cart_size.text)


class OrderPage(TestCase):

    def setUp(self):
        """Sets up testing url and dispatches selenium webdriver."""
        def buy_five_products():
            self.browser.maximize_window()
            self.browser.get(settings.LOCALHOST +
                             'catalog/categories/akkumuliatory/')
            for i in range(1, 6):
                self.browser.find_element_by_xpath(
                    '//*[@id="products-wrapper"]/div[{}]/div[2]/div[5]/button'
                    .format(i)
                ).click()
        self.browser = webdriver.Chrome()
        self.browser.maximize_window()
        self.browser.implicitly_wait(10)
        buy_five_products()
        self.browser.get(settings.LOCALHOST + 'shop/order/')
        self.cart_dropdown = self.browser.find_element_by_class_name(
            'basket-parent')

    def tearDown(self):
        """Closes selenium's session."""
        self.browser.quit()

    def test_table_is_presented_if_there_is_some_products(self):
        """If there are some products in cart, we should see them in table on OrderPage."""
        order_table = self.browser.find_element_by_class_name('order-list')
        self.assertTrue(order_table.is_displayed())

    def test_remove_product_from_table(self):
        """We can remove product from table and see the changes both in table and dropdown."""
        first_row_remove = self.browser.find_element_by_xpath(
            '//*[@id="4023"]/td[6]/img')
        first_row_product_name = self.browser.find_element_by_xpath(
            '//*[@id="4023"]/td[3]/a').text
        first_row_remove.click()
        wait()
        self.assertFalse(
            first_row_product_name in self.browser.find_element_by_class_name('order-list').text)
        hover(self.browser, self.cart_dropdown)
        dropdown_products_list = self.browser.find_element_by_class_name(
            'basket-list')
        self.assertFalse(first_row_product_name in dropdown_products_list.text)

    def test_empty_cart(self):
        products_in_cart = ['4526', '4023', '4524', '4523']
        for product_id in products_in_cart:
            self.browser.find_element_by_xpath(
                '//*[@id="{}"]/td[6]/img'.format(product_id)
            ).click()
            wait()

        self.assertFalse('Корзина пуста' in self.browser.find_element_by_class_name(
            'js-order-contain').text)

    def test_table_and_dropdown_are_synchronized(self):
        def get_counts():
            return (self.browser.find_element_by_id('cart-page-prods-count').text,
                    self.browser.find_element_by_class_name('js-cart-size').text)

        self.browser.refresh()
        table_count, dropdown_count = get_counts()
        self.assertEqual(table_count, '5')
        self.assertEqual(dropdown_count, table_count)
        self.browser.find_element_by_xpath(
            '//*[@id="4526"]/td[4]/div[2]/span[3]/button[1]/i').click()
        wait()
        table_count, dropdown_count = get_counts()
        self.assertEqual(table_count, '6')
        self.assertEqual(table_count, dropdown_count)
        wait()
        self.browser.find_element_by_xpath(
            '//*[@id="4526"]/td[6]/img').click()
        wait()
        table_count, dropdown_count = get_counts()
        self.assertEqual(table_count, dropdown_count)
        self.assertEqual(table_count, '4')

    def test_change_product_count(self):
        """
        We can change product's count from table and see the changes both in table and dropdown.
        """
        add_one_more = self.browser.find_element_by_xpath(
            '//*[@id="4023"]/td[4]/div[2]/span[3]/button[1]/i')
        add_one_more.click()
        wait()
        count_input = self.browser.find_element_by_xpath(
            '//*[@id="4023"]/td[4]/div[2]/input')
        product_count, total_count = '2', '6'
        self.assertTrue(product_count in count_input.get_attribute('value'))
        self.assertTrue(
            total_count in self.browser.find_element_by_class_name('js-cart-size').text)

    def test_confirm_order(self):
        """After filling the form we should be able to confirm an order."""
        self.browser.find_element_by_id('id_payment_option_0').click()
        add_one_more = self.browser.find_element_by_xpath(
            '//*[@id="4023"]/td[4]/div[2]/span[3]/button[1]/i')
        add_one_more.click()  # perform some operations on cart
        wait()
        self.fill_and_submit_form()
        wait()
        self.assertEqual(self.browser.current_url, success_order_page)

    def fill_and_submit_form(self, yandex=False):
        self.browser.find_element_by_id('id_name').send_keys('Name')
        self.browser.find_element_by_id('id_city').send_keys('Санкт-Петербург')
        self.browser.find_element_by_id('id_phone').send_keys('22222222222')
        self.browser.find_element_by_id('id_email').send_keys('test@test.test')
        wait()
        submit = 'btn-send-ya' if yandex else 'btn-send-se'
        self.browser.find_element_by_id(submit).click()

    def test_yandex_order_without_phone(self):
        self.browser.find_element_by_id('id_payment_option_2').click()
        self.browser.find_element_by_id('id_name').send_keys('Name')
        self.browser.find_element_by_id('id_city').send_keys('Санкт-Петербург')
        self.browser.find_element_by_id('btn-send-ya').click()
        wait()
        alert = self.browser.switch_to.alert
        self.assertIn('телефон', alert.text)

    def test_yandex_order(self):
        self.browser.find_element_by_id('id_payment_option_2').click()
        self.fill_and_submit_form(yandex=True)
        wait()
        yandex_order = settings.LOCALHOST + 'test-ya-kassa/'
        self.assertEqual(self.browser.current_url, yandex_order)


class BlogPageSeleniumTests(TestCase):
    """
    Selenium-based tests for product page UI.
    """

    def setUp(self):
        """Sets up testing url and dispatches selenium webdriver."""

        self.test_blog_root_page = settings.LOCALHOST + 'blog/'
        self.test_blog_pages_list = settings.LOCALHOST + 'blog/posts/article/'
        self.test_blog_page = settings.LOCALHOST + 'blog/contacts/'
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(20)

    def tearDown(self):
        """Closes selenium's session."""

        self.browser.quit()

    @property
    def _accordion_title(self):
        return self.browser.find_element_by_id('js-accordion-title-navigation')

    @property
    def accordion_content(self):
        return self.browser.find_element_by_id(
            'js-accordion-content-navigation')

    def test_accordion_minimized(self):
        """Accordion item should be minimized by default"""

        self.browser.get(self.test_blog_page)
        wait()
        self.assertFalse(self.accordion_content.is_displayed())

    def test_accordion_expand(self):
        """Accordion item should expand by click on title"""

        self.browser.get(self.test_blog_page)
        accordion_title = self._accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        wait()
        self.assertTrue(accordion_content.is_displayed())

    def test_accordion_minimize_by_double_click(self):
        """Accordion item should be minimized by two clicks on title"""

        self.browser.get(self.test_blog_page)
        accordion_title = self._accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        wait()
        accordion_title.click()
        wait()
        self.assertFalse(accordion_content.is_displayed())


class AdminPageSeleniumTests(TestCase):
    """
    Selenium-based tests for Admin page UI.
    """

    def setUp(self):
        """
        Sets up testing url and dispatches selenium webdriver.
        """

        self.admin_page = settings.LOCALHOST + 'admin'
        self.login = settings.ADMIN_LOGIN
        self.password = settings.ADMIN_PASS
        self.title_text = 'Shopelectro administration'
        self.products_list_link = '//*[@id="content-main"]/div[5]/table/tbody/tr/th/a'
        self.product_price_filter_link = '//*[@id="changelist-filter"]/ul[1]/li[4]'
        self.show_active_products_link = '//*[@id="changelist-filter"]/ul[2]/li[2]/a'
        self.show_nonactive_products_link = '//*[@id="changelist-filter"]/ul[2]/li[3]/a'
        self.products_activity_state_img = '//*[@id="result_list"]/tbody/tr[1]/td[6]/img'
        self.autocomplete_text = 'Фонарь'
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(5)
        self.browser.maximize_window()

        self.browser.get(self.admin_page)
        login_field = self.browser.find_element_by_id('id_username')
        login_field.clear()
        login_field.send_keys(self.login)
        password_field = self.browser.find_element_by_id('id_password')
        password_field.clear()
        password_field.send_keys(self.password)
        login_form = self.browser.find_element_by_id('login-form')
        login_form.submit()
        wait()

    def tearDown(self):
        """
        Closes selenium's session.
        """

        self.browser.quit()

    def go_to_products_list(self):
        products_link = self.browser.find_element_by_xpath(self.products_list_link)
        products_link.click()
        time.sleep(1)

    def test_login(self):
        """
        We are able to login to Admin page.
        """
        admin_title = self.browser.find_element_by_id('site-name')
        self.assertIn(self.title_text, admin_title.text)

    def test_admin_product(self):
        """
        Admin products page has icon links for Edit\View.
        And it should has Search field.
        """
        self.go_to_products_list()
        edit_links = self.browser.find_element_by_class_name('field-links')
        search_field = self.browser.find_element_by_id('changelist-search')
        self.assertTrue(edit_links)
        self.assertTrue(search_field)

    def test_product_price_filter(self):
        """
        Price filter is able to filter products by set range.
        In this case we filter products with 1000 - 2000 price range.
        """
        self.go_to_products_list()

        filter_link = self.browser.find_element_by_xpath(
            self.product_price_filter_link)
        filter_link.click()
        wait()
        first_product = self.browser.find_element_by_id('id_form-0-price')
        first_product_price = float(first_product.get_attribute('value'))

        self.assertTrue(first_product_price >= 1000)

    def test_filter_active_items(self):
        """
        Activity filter returns only active or non active items.
        """
        self.go_to_products_list()

        filter_link = self.browser.find_element_by_xpath(
            self.show_active_products_link)
        filter_link.click()
        wait()
        first_product = self.browser.find_element_by_xpath(
            self.products_activity_state_img)
        first_product_state = first_product.get_attribute('alt')

        self.assertTrue(first_product_state == 'true')

    def test_is_active_filter(self):
        """
        Activity filter returns only active or non active items.
        """
        self.go_to_products_list()
        wait()

        filter_link = self.browser.find_element_by_xpath(
            self.show_active_products_link)
        filter_link.click()
        wait()
        first_product = self.browser.find_element_by_xpath(
            self.products_activity_state_img)
        first_product_state = first_product.get_attribute('alt')

        self.assertTrue(first_product_state == 'true')

        filter_link = self.browser.find_element_by_xpath(
            self.show_nonactive_products_link)
        filter_link.click()
        wait()
        results = self.browser.find_element_by_class_name('paginator')
        self.assertTrue('0' in results.text)

    def test_search_autocomplete(self):
        """
        Search field could autocomplete.
        """
        self.go_to_products_list()

        filter_link = self.browser.find_element_by_id('searchbar')
        filter_link.send_keys(self.autocomplete_text)
        wait()
        first_suggested_item = self.browser.find_element_by_class_name(
            'autocomplete-suggestion')
        first_suggested_item_text = first_suggested_item.get_attribute(
            'data-val')

        self.assertTrue(self.autocomplete_text in first_suggested_item_text)


class YandexKassa(TestCase):

    def setUp(self):
        self.browser = Chrome()
        self.yandex_check = settings.LOCALHOST + 'service/ya-kassa/check/'
        self.yandex_aviso = settings.LOCALHOST + 'service/ya-kassa/aviso/'

    def tearDown(self):
        self.browser.quit()

    def test_yandex_check_valid_invoice(self):
        response = self.browser.request('POST',
                                        self.yandex_check,
                                        data={"invoiceId": "42"})
        self.assertTrue('invoiceId="42"' in response.text)


class SitemapPageTests(TestCase):
    """
    Tests for Sitemap.
    Getting sitemap.xml and parsing it as string.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Import testing data into DB and create site domain name.
        """
        call_command('catalog')
        call_command('redirects')

        # Namespace for using ET.find()
        cls.NAMESPACE = '{http://www.sitemaps.org/schemas/sitemap/0.9}'

    @classmethod
    def tearDownClass(cls):
        """
        Remove data.
        """
        os.remove('priceru.xml')
        os.remove('yandex.yml')
        os.remove('pricelist.xlsx')

    def setUp(self):
        """
        Sets up testing url.
        """

        content = self.client.get('/sitemap.xml').content.decode('utf-8')
        self.root = ET.fromstring(content)

    def test_url_tags(self):
        """
        We should see <url> tags on Sitemap page.
        """
        url_tags = self.root.findall("{}url".format(self.NAMESPACE))
        self.assertGreater(len(url_tags), 0)

    def test_models_urls(self):
        """
        Sitemap page should to print correct urls for models.
        """
        slice_start_index = len("http://" + settings.SITE_DOMAIN_NAME)

        path = "{0}url[2]/{0}loc".format(self.NAMESPACE)
        model_url_text = self.root.find(path).text[slice_start_index:]

        response = self.client.get(model_url_text)

        self.assertEqual(response.status_code, 200)
