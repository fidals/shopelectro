"""
Selenium-based tests.

If you need to create new test-suite, subclass it from SeleniumTestCase class.
Every Selenium-based test suite uses fixture called dump.json.
"""

import time

from selenium.webdriver.common.keys import Keys
from seleniumrequests import Chrome  # We use this instead of standard selenium
from selenium.webdriver.common.action_chains import ActionChains

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from blog.models import Post


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


def hover(browser, element):
    """Perform a hover over an element."""
    hover_action = ActionChains(browser).move_to_element(element)
    hover_action.perform()


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""
    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super(SeleniumTestCase, cls).setUpClass()
        cls.browser = Chrome()
        cls.browser.implicitly_wait(5)
        cls.browser.maximize_window()

    @classmethod
    def tearDownClass(cls):
        """Closes selenium's session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()


class Header(SeleniumTestCase):
    """Selenium-based tests for header."""

    def setUp(self):
        """Sets up testing urls and dispatches selenium webdriver."""
        self.browser.get(self.live_server_url)

    @property
    def call_button(self):
        return self.browser.find_element_by_class_name(
            'feedback-but-btn')

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
        wait()
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


class CategoryPage(SeleniumTestCase):
    """Selenium-based tests for Category Page."""

    @classmethod
    def setUpClass(cls):
        """Sets up testing urls."""
        super(CategoryPage, cls).setUpClass()
        server = cls.live_server_url
        testing_url = lambda alias: server + reverse('category', args=[alias])
        cls.direct_child = testing_url('child-1-of-root-category-1')
        cls.deep_category = testing_url('child-2-of-child-2-'
                                        'of-root-category-1')
        cls.root_category = testing_url('root-category-1')

    @property
    def load_more_button(self):
        return self.browser.find_element_by_id('btn-load-products')

    def test_breadcrumbs(self):
        """
        Breadcrumbs should be presented on every category page.
        Their count depends on category's depth in a catalog tree.
        For the root categories, for example, there should be 3 crumbs.
        :return:
        """

        # In 'root category' there should be three crumbs
        self.browser.get(self.root_category)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 3)

        # In 'deep category' there should be more crumbs
        self.browser.get(self.deep_category)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 5)

    def test_30_products_by_default(self):
        """By default any CategoryPage should contain 30 products."""

        self.browser.get(self.root_category)
        loaded_products = self.browser.find_element_by_class_name(
            'js-products-showed-count').text
        self.assertEqual('30', loaded_products)

    def test_load_more_products(self):
        """
        We can load another 30 by clicking load more button.

        After that we wait some time for XHR will be performed
        and there will be new count of loaded products.
        """

        self.browser.get(self.root_category)
        self.browser.refresh()
        self.load_more_button.click()  # Let's load another 30 products.
        wait()
        loaded_products_count = self.browser.find_element_by_class_name(
            'js-products-showed-count').text
        self.assertEqual('60', loaded_products_count)

    def test_load_more_hidden_in_fully_loaded_categories(self):
        """
        If category has less products than LOAD_LIMIT
        we shouldn't see load more button.
        """

        self.browser.get(self.deep_category)
        self.assertTrue(
            'hidden' in self.load_more_button.get_attribute('class'))

    def test_default_view_is_tile(self):
        """
        By default, category page should has tile view

        It means, after rendering a page,
        tile view selector should has 'active' class
        and category wrapper 'view-mode-tile' class.
        """

        self.browser.get(self.direct_child)
        tile_view_selector = self.browser.find_element_by_class_name(
            'js-icon-mode-tile')
        products_view = self.browser.find_element_by_id('category-right')
        self.assertTrue('active' in
                        tile_view_selector.get_attribute('class'))
        self.assertTrue('view-mode-tile' in
                        products_view.get_attribute('class'))

    def test_change_view(self):
        """
        We should be able to change default view
        to list view without reloading a page.
        """

        self.browser.get(self.direct_child)
        list_view_selector = self.browser.find_element_by_class_name(
            'js-icon-mode-list')
        products_view = self.browser.find_element_by_id('category-right')

        self.assertFalse('active' in
                         list_view_selector.get_attribute('class'))
        self.assertFalse('view-mode-list' in
                         products_view.get_attribute('class'))

        list_view_selector.click()
        self.assertTrue('active' in
                        list_view_selector.get_attribute('class'))
        self.assertTrue('view-mode-list' in
                        products_view.get_attribute('class'))

    def test_default_sorting_is_by_cheapest(self):
        """By default, sorting should be by cheapest goods."""

        self.browser.get(self.direct_child)
        cheapest_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/'
            'div[1]/div/div/div[2]/label/div/select/option[1]')
        self.assertTrue(cheapest_sort_option.is_selected())

    def test_change_sorting(self):
        """We can change sorting option"""
        self.browser.get(self.direct_child)
        expensive_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/'
            'div[1]/div/div/div[2]/label/div/select/option[3]'
        )
        expensive_sort_option.click()
        expensive_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/'
            'div[1]/div/div/div[2]/label/div/select/option[3]'
        )
        self.assertTrue(expensive_sort_option.is_selected())

    def test_add_to_cart(self):
        """We can add item to cart from it's category page."""
        self.browser.get(self.direct_child)
        self.browser.find_elements_by_class_name(
            'js-product-to-cart')[0].click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name(
            'js-cart-is-empty')
        self.assertFalse(cart_is_empty.is_displayed())


class ProductPage(SeleniumTestCase):
    """
    Selenium-based tests for product page UI.
    """

    fixtures = ['dump.json']

    def setUp(self):
        """Sets up testing url and dispatches selenium webdriver."""

        server = self.live_server_url

        self.test_product_page = server + reverse('product', args=['1'])
        self.success_order = server + reverse('ecommerce:order_success')
        self.product_name = 'Product of Child #0 of #Root category #0'
        self.browser.get(self.test_product_page)
        self.one_click = self.browser.find_element_by_id('btn-one-click-order')

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
        self.assertEqual(self.browser.current_url, self.success_order)

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
        self.assertTrue(self.product_name in cart.text)

    def test_actual_product_count_in_cart_dropdown(self):
        self.browser.find_element_by_id('product-count').send_keys('42')
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        hover(self.browser, cart_parent)
        cart_size = self.browser.find_element_by_class_name('js-cart-size')
        self.assertTrue('42' in cart_size.text)


class OrderPage(SeleniumTestCase):

    @classmethod
    def setUpClass(cls):
        super(OrderPage, cls).setUpClass()
        cls.category = reverse('category', args=(
            'child-1-of-root-category-1',))
        cls.cart_dropdown = 'basket-parent'
        cls.first_product_id = '99'
        cls.remove_product = '//*[@id="{}"]/td[6]/img'
        cls.product_count = '//*[@id="{}"]/td[4]/div[2]/input'
        cls.add_product = '//*[@id="{}"]/td[4]/div[2]/span[3]/button[1]/i'

    def setUp(self):
        self.__buy_products()
        self.browser.get(self.live_server_url +
                         reverse('ecommerce:order_page'))

    def __buy_products(self):
        self.browser.get(self.live_server_url + self.category)
        for i in range(1, 6):
            self.browser.find_element_by_xpath(
                '//*[@id="products-wrapper"]/div[{}]/div[2]/div[5]/button'
                .format(i)
            ).click()

    def test_table_is_presented_if_there_is_some_products(self):
        """
        If there are some products in cart,
        we should see them in table on OrderPage.
        """
        order_table = self.browser.find_element_by_class_name('order-list')
        self.assertTrue(order_table.is_displayed())

    def test_remove_product_from_table(self):
        """We can remove product from table and see the changes immediately."""
        first_row_remove = self.browser.find_element_by_xpath(
            self.remove_product.format(self.first_product_id))
        first_row_remove.click()
        wait()
        self.assertFalse(
            self.first_product_id in
            self.browser.find_element_by_class_name('order-list').text)

    def test_empty_cart(self):
        """
        After removing every product from cart
        we should see that it is empty.
        """
        removes = self.browser.find_elements_by_class_name('js-remove')
        while removes:
            remove = removes[0]
            remove.click()
            wait()
            removes = self.browser.find_elements_by_class_name('js-remove')

        self.assertTrue('Корзина пуста' in
                        self.browser.find_element_by_class_name(
                            'js-order-contain').text)

    def test_table_and_dropdown_are_synchronized(self):
        def get_counts():
            table_count = (self.browser
                           .find_element_by_id('cart-page-prods-count')
                           .text)
            header_count = (self.browser
                            .find_element_by_class_name('js-cart-size')
                            .text)
            return table_count, header_count

        self.browser.refresh()
        table_count, dropdown_count = get_counts()
        self.assertEqual(table_count, '5')
        self.assertEqual(dropdown_count, table_count)
        self.browser.find_element_by_xpath(
            self.add_product.format(self.first_product_id)).click()
        wait()
        table_count, dropdown_count = get_counts()
        self.assertEqual(table_count, '6')
        self.assertEqual(table_count, dropdown_count)
        wait()
        self.browser.find_element_by_xpath(
            self.remove_product.format(self.first_product_id)).click()
        wait()
        table_count, dropdown_count = get_counts()
        self.assertEqual(table_count, dropdown_count)
        self.assertEqual(table_count, '4')

    def test_change_product_count(self):
        """
        We can change product's count from table
        and see the changes both in table and dropdown.
        """
        add_one_more = self.browser.find_element_by_xpath(
            self.add_product.format(self.first_product_id))
        add_one_more.click()
        wait()
        count_input = self.browser.find_element_by_xpath(
            self.product_count.format(self.first_product_id))
        product_count, total_count = '2', '6'
        self.assertTrue(product_count in count_input.get_attribute('value'))
        self.assertTrue(total_count in
                        self.browser
                        .find_element_by_class_name('js-cart-size').text)

    def test_confirm_order(self):
        """After filling the form we should be able to confirm an order."""
        self.browser.find_element_by_id('id_payment_option_0').click()
        add_one_more = self.browser.find_element_by_xpath(
            self.add_product.format(self.first_product_id))
        add_one_more.click()  # perform some operations on cart
        wait()
        self.fill_and_submit_form()
        wait()
        self.assertEqual(self.browser.current_url,
                         self.live_server_url +
                         reverse('ecommerce:order_success'))

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
        self.browser.find_element_by_id('id_phone').clear()
        self.browser.find_element_by_id('btn-send-ya').click()
        wait()
        alert = self.browser.switch_to.alert
        self.assertIn('телефон', alert.text)


class BlogPageSeleniumTests(SeleniumTestCase):
    """
    Selenium-based tests for product page UI.
    """

    @classmethod
    def setUpClass(cls):
        super(BlogPageSeleniumTests, cls).setUpClass()

        # TODO: Duke, how it can be reversed?
        cls.test_blog_page = (cls.live_server_url +
                              '/blog/contacts/')

    def setUp(self):
        Post.objects.create(name='contacts')
        self.browser.get(self.test_blog_page)
        self.browser.execute_script('localStorage.clear();')
        self.browser.get(self.test_blog_page)
        wait()

    @property
    def _accordion_title(self):
        return self.browser.find_element_by_id('js-accordion-title-navigation')

    @property
    def accordion_content(self):
        return self.browser.find_element_by_id(
            'js-accordion-content-navigation')

    def test_accordion_minimized(self):
        """Accordion item should be minimized by default"""
        self.assertFalse(self.accordion_content.is_displayed())

    def test_accordion_expand(self):
        """Accordion item should expand by click on title"""
        accordion_title = self._accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        wait()
        self.assertTrue(accordion_content.is_displayed())

    def test_accordion_minimize_by_double_click(self):
        """Accordion item should be minimized by two clicks on title"""
        accordion_title = self._accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        wait()
        accordion_title.click()
        wait()
        self.assertFalse(accordion_content.is_displayed())


class AdminPageSeleniumTests(SeleniumTestCase):
    """
    Selenium-based tests for Admin page UI.
    """

    fixtures = ['dump.json', 'admin.json']

    @classmethod
    def setUpClass(cls):
        super(AdminPageSeleniumTests, cls).setUpClass()
        cls.admin_page = cls.live_server_url + reverse('admin:index')
        cls.login = 'admin'
        cls.password = 'asdfjkl;'
        cls.title_text = 'Shopelectro administration'
        cls.products = '//*[@id="content-main"]/div[5]/table/tbody/tr/th/a'
        cls.price_filter = '//*[@id="changelist-filter"]/ul[1]/li[4]'
        cls.active_products = '//*[@id="changelist-filter"]/ul[2]/li[2]/a'
        cls.inactive_products = '//*[@id="changelist-filter"]/ul[2]/li[3]/a'
        cls.is_active_img = '//*[@id="result_list"]/tbody/tr[1]/td[6]/img'
        cls.autocomplete_text = 'Prod'

    def setUp(self):
        """
        Sets up testing url and dispatches selenium webdriver.
        """
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

    def test_login(self):
        """
        We are able to login to Admin page.
        """
        admin_title = self.browser.find_element_by_id('site-name')
        self.assertIn(self.title_text, admin_title.text)

    def test_admin_product(self):
        """
        Admin products page has icon links for Edit and View.
        And it should has Search field.
        """
        products_link = self.browser.find_element_by_xpath(
            self.products)
        products_link.click()
        wait()
        edit_links = self.browser.find_element_by_class_name('field-links')
        search_field = self.browser.find_element_by_id('changelist-search')
        self.assertTrue(edit_links)
        self.assertTrue(search_field)

    def test_product_price_filter(self):
        """
        Price filter is able to filter products by set range.
        In this case we filter products with 1000 - 2000 price range.
        """
        products_link = self.browser.find_element_by_xpath(
            self.products)
        products_link.click()
        wait()

        filter_link = self.browser.find_element_by_xpath(
            self.price_filter)
        filter_link.click()
        wait()
        first_product = self.browser.find_element_by_id('id_form-0-price')
        first_product_price = float(first_product.get_attribute('value'))

        self.assertTrue(first_product_price >= 1000)

    def test_is_active_filter(self):
        """
        Activity filter returns only active or non active items.
        """
        products_link = self.browser.find_element_by_xpath(
            self.products)
        products_link.click()
        wait()

        filter_link = self.browser.find_element_by_xpath(
            self.active_products)
        filter_link.click()
        wait()
        first_product = self.browser.find_element_by_xpath(
            self.is_active_img)
        first_product_state = first_product.get_attribute('alt')

        self.assertTrue(first_product_state == 'true')

        filter_link = self.browser.find_element_by_xpath(
            self.inactive_products)
        filter_link.click()
        wait()
        results = self.browser.find_element_by_class_name('paginator')
        self.assertTrue('0' in results.text)

    def test_search_autocomplete(self):
        """
        Search field could autocomplete.
        """
        products_link = self.browser.find_element_by_xpath(
            self.products)
        products_link.click()
        wait()

        filter_link = self.browser.find_element_by_id('searchbar')
        filter_link.send_keys(self.autocomplete_text)
        wait()
        first_suggested_item = self.browser.find_element_by_class_name(
            'autocomplete-suggestion')
        first_suggested_item_text = first_suggested_item.get_attribute(
            'data-val')

        self.assertTrue(self.autocomplete_text in first_suggested_item_text)


class YandexKassa(SeleniumTestCase):

    @classmethod
    def setUpClass(cls):
        super(YandexKassa, cls).setUpClass()
        cls.yandex_check = cls.live_server_url + reverse('yandex_check')
        cls.yandex_aviso = cls.live_server_url + reverse('yandex_aviso')

    def test_yandex_check_valid_invoice(self):
        response = self.browser.request('POST',
                                        self.yandex_check,
                                        data={"invoiceId": "42"})
        self.assertTrue('invoiceId="42"' in response.text)


class SearchTests(SeleniumTestCase):
    """Selenium-based tests for Search"""

    def setUp(self):
        self.browser.get(self.live_server_url)
        wait()
        self.input = self.browser.find_element_by_class_name('js-search-input')
        self.autocomplete = self.browser.find_element_by_class_name(
            'autocomplete-suggestions')
        self.query = 'Cate'

    def fill_input(self):
        """Enter correct search term"""

        self.input.send_keys(self.query)
        wait()

    def test_autocomplete_can_expand_and_collapse(self):
        """
        Autocomplete should minimize during user typing correct search query
        Autocomplete should minimize by removing search query
        """
        self.fill_input()
        # fill input and autocomplete expands
        self.assertTrue(self.autocomplete.is_displayed())

        # remove search term ...
        self.input.send_keys(Keys.BACKSPACE * len(self.query))
        wait()
        # ... and autocomplete collapse
        self.assertFalse(self.autocomplete.is_displayed())

    def test_autocomplete_item_link(self):
        """First autocomplete item should link on category page by click"""

        self.fill_input()
        first_item = self.autocomplete.find_element_by_css_selector(
            ':first-child')
        first_item.click()
        wait()
        self.assertTrue('/catalog/category/' in self.browser.current_url)

    def test_autocomplete_see_all_item(self):
        """
        Autocomplete should contain "see all" item.
        "See all" item links on search results page
        """

        self.fill_input()
        last_item = self.autocomplete.find_element_by_class_name(
            'autocomplete-last-item')
        last_item.click()
        wait()
        self.assertTrue('/search/' in self.browser.current_url)

    def test_search_have_results(self):
        """Search results page should contain links on relevant pages"""

        self.fill_input()
        search_form = self.browser.find_element_by_class_name('search-form')
        search_form.submit()
        wait()
        self.assertTrue(self.browser.find_element_by_link_text(
            'Child #0 of #Root category #0'))
        self.assertTrue(self.browser.find_element_by_link_text(
            'Child #1 of #Root category #0'))

    def test_search_results_empty(self):
        """Search results for wrong term should contain empty result set"""

        self.input.send_keys('Not existing search query')
        button_submit = self.browser.find_element_by_id('search-submit')
        button_submit.click()
        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertTrue(h1.text == 'По вашему запросу ничего не найдено')
