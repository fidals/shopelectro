"""
Selenium-based tests.

If you need to create new test-suite, subclass it from SeleniumTestCase class.
Every Selenium-based test suite uses fixture called dump.json.
"""

import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from seleniumrequests import Chrome  # We use this instead of standard selenium

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.test import LiveServerTestCase
from django.test.utils import override_settings

from pages.models import FlatPage, CustomPage, Page

from shopelectro.models import Category, Product


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


def hover(browser, element):
    """Perform a hover over an element."""
    ActionChains(browser).move_to_element(element).perform()


def context_click(browser, element):
    ActionChains(browser).context_click(element).perform()
    wait()


def make_backcall(browser):
    """Trigger backcall modal. Fill it and submit."""
    browser.find_element_by_class_name('js-backcall-order').click()
    wait()
    browser.find_element_by_id('back-call-phone').send_keys('22222222222')
    browser.find_element_by_xpath(
        '//*[@id="back-call-time"]/option[3]').click()
    wait()
    browser.find_element_by_class_name('js-send-backcall').click()
    wait()


def show_cart_dropdown(browser):
    cart_parent = browser.find_element_by_class_name('basket-parent')
    hover(browser, cart_parent)
    wait()


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
        """Close selenium session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()


@override_settings(DEBUG=True)
class Header(SeleniumTestCase):

    def setUp(self):
        """Set up testing urls and dispatch selenium webdriver."""
        self.browser.get(self.live_server_url)

    def test_call_modal_not_visible(self):
        """By default we shouldn't see call modal."""
        modal = self.browser.find_element_by_id('back-call-modal')

        self.assertFalse(modal.is_displayed())

    def test_order_backcall(self):
        """After filling modal fields user can successfully order backcall."""
        make_backcall(self.browser)

        self.assertTrue(self.browser.find_element_by_class_name(
            'js-backcall-success').is_displayed())

    def test_empty_cart(self):
        """By default there should be 'Корзина пуста' in the header's cart."""
        cart_in_header = self.browser.find_element_by_class_name(
            'js-header-cart')

        self.assertTrue('Корзина пуста' in cart_in_header.text)

    def test_cart_hover(self):
        """Cart dropdown should be visible on hover."""
        show_cart_dropdown(self.browser)
        cart = self.browser.find_element_by_class_name('basket-wrapper')

        self.assertTrue(cart.is_displayed())

    def test_cart_flush(self):
        """We can flush cart from header's cart dropdown"""
        product_id = Product.objects.first().id
        self.browser.get(self.live_server_url + reverse('product', args=(product_id,)))
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        show_cart_dropdown(self.browser)
        self.browser.find_element_by_class_name('basket-reset').click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name('js-cart-is-empty')

        self.assertTrue(cart_is_empty.is_displayed())


class CategoryPage(SeleniumTestCase):

    def setUp(self):
        server = self.live_server_url
        self.testing_url = lambda slug: server + reverse('category', args=(slug,))

        root_category = Category.objects.filter(parent=None).first()
        children_category = Category.objects.filter(parent=root_category).first()
        category_with_product_less_then_LOAD_LIMIT = Category.objects.annotate(
            prod_count=Count('products')).exclude(prod_count=0).filter(
            prod_count__lt=settings.PRODUCTS_TO_LOAD).first()

        self.root_category = self.testing_url(root_category.page.slug)
        self.children_category = self.testing_url(children_category.page.slug)
        self.deep_children_category = self.testing_url(
            category_with_product_less_then_LOAD_LIMIT.page.slug)

    @property
    def load_more_button(self):
        return self.browser.find_element_by_id('btn-load-products')

    def test_breadcrumbs(self):
        """
        Breadcrumbs should be presented on every category page.
        Their count depends on category's depth in a catalog tree.
        For the root categories, for example, there should be 3 crumbs.
        """
        # There should be three crumbs in 'root category'.
        self.browser.get(self.root_category)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')

        self.assertEqual(len(crumbs), 3)

        # In 'deep category' there should be more crumbs
        self.browser.get(self.children_category)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')

        self.assertEqual(len(crumbs), 4)

    def test_30_products_by_default(self):
        """Any CategoryPage should contain 30 products by default."""
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
        we shouldn't see `Load more` button.
        """
        self.browser.get(self.deep_children_category)
        wait()

        self.assertTrue('hidden' in self.load_more_button.get_attribute('class'))

    def test_default_view_is_tile(self):
        """
        By default, category page should has tile view.

        It means, after rendering a page,
        tile view selector should has 'active' class
        and category wrapper 'view-mode-tile' class.
        """
        self.browser.get(self.children_category)
        tile_view_selector = self.browser.find_element_by_class_name(
            'js-icon-mode-tile')
        products_view = self.browser.find_element_by_id('category-right')

        self.assertTrue('active' in tile_view_selector.get_attribute('class'))
        self.assertTrue('view-mode-tile' in products_view.get_attribute('class'))

    def test_change_view(self):
        """
        We should be able to change default view
        to list view without reloading a page.
        """
        self.browser.get(self.children_category)
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
        self.browser.get(self.children_category)
        cheapest_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/'
            'div[1]/div/div/div[2]/label/div/select/option[1]')

        self.assertTrue(cheapest_sort_option.is_selected())

    def test_change_sorting(self):
        """We can change sorting option"""
        self.browser.get(self.children_category)
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
        self.browser.get(self.children_category)
        self.browser.find_elements_by_class_name(
            'js-product-to-cart')[0].click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name(
            'js-cart-is-empty')

        self.assertFalse(cart_is_empty.is_displayed())

    def test_add_to_cart_after_load_more(self):
        """
        We are able to add loaded product to Cart after Load more button click on
        Category page.
        """
        self.browser.get(self.root_category)
        self.browser.refresh()
        wait()
        self.load_more_button.click()  # Let's load another 30 products.
        wait(15)
        recently_loaded_product = self.browser.find_elements_by_class_name(
            'js-product-to-cart')[settings.PRODUCTS_TO_LOAD + 1]
        recently_loaded_product.click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name(
            'js-cart-is-empty')

        self.assertFalse(cart_is_empty.is_displayed())


class ProductPage(SeleniumTestCase):

    PRODUCT_ID = 1

    def setUp(self):
        """Set up testing url and dispatch selenium webdriver."""
        product = Product.objects.get(id=self.PRODUCT_ID)
        server = self.live_server_url
        self.test_product_page = server + reverse('product', args=(product.id,))
        self.success_order = server + reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order-success',))
        self.product_name = product.name
        self.browser.get(self.test_product_page)
        self.one_click = self.browser.find_element_by_id('btn-one-click-order')

    def test_breadcrumbs(self):
        """
        Breadcrumbs should be presented on every product page.
        Their count depends on product's depth in a catalog tree.
        """
        # There should be 6 items in breadcrumbs for this case
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')

        self.assertEqual(len(crumbs), 6)

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
        self.browser.find_element_by_id('product-image-big').click()
        wait()
        fancybox_wrap = self.browser.find_element_by_class_name('fancybox-wrap')

        self.assertTrue(fancybox_wrap)

    def test_images_switch(self):
        """If product has > 1 image, we could to switch them by clicking."""
        def get_main_image_src():
            image = self.browser.find_element_by_id('product-image-big')
            wait()
            return image.get_attribute('src')

        not_switched_path = get_main_image_src()

        image_preview = self.browser.find_element_by_xpath('//*[@id="product-images"]/div[2]/img')
        image_preview.click()
        wait()
        switched_path = get_main_image_src()

        self.assertNotEquals(not_switched_path, switched_path)

    def test_one_click_buy_disabled_with_empty_phone(self):
        """By default .btn-one-click-order should be disabled"""
        self.browser.find_element_by_id(
            'input-one-click-phone').send_keys(Keys.BACKSPACE)

        self.assertTrue(self.one_click.get_attribute('disabled'))

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
        cart_is_empty = self.browser.find_element_by_class_name('js-cart-is-empty')

        self.assertFalse(cart_is_empty.is_displayed())

    def test_product_name_in_cart_dropdown(self):
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        show_cart_dropdown(self.browser)
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        cart = cart_parent.find_element_by_class_name('basket-wrapper')

        self.assertTrue(self.product_name in cart.text)

    def test_actual_product_count_in_cart_dropdown(self):
        self.browser.find_element_by_id('product-count').send_keys('42')
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        show_cart_dropdown(self.browser)
        cart_size = self.browser.find_element_by_class_name('js-cart-size')

        self.assertTrue('42' in cart_size.text)


class OrderPage(SeleniumTestCase):

    @staticmethod
    def get_cell(pos, col):
        # table columns mapping: http://prntscr.com/bsv5hp
        COLS = {
            'id': 1,
            'name': 3,
            'count': 4,
            'price': 5,
            'remove': 6,
        }
        product_row = '//*[@id="js-order-list"]/tbody/tr[{pos}]/td[{col}]'

        return product_row.format(pos=pos, col=COLS[col])

    def setUp(self):
        self.order_page = CustomPage.objects.get(slug='order')
        self.cart_dropdown = 'basket-parent'
        self.first_product_id = '405'
        self.remove_product = self.get_cell(pos=4, col='remove') + '/img'
        self.product_count = self.get_cell(pos=4, col='count') + '/div[2]/input'
        self.add_product = self.get_cell(pos=4, col='count') + '/div[2]/span[3]/button[1]'
        self.category = reverse('category', args=(Category.objects.first().page.slug,))
        self.buy_products()
        wait()
        self.browser.get(self.live_server_url + self.order_page.url)

    def buy_products(self):
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
            self.remove_product)
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
                           .find_element_by_id('cart-page-prods-count').text)
            header_count = (self.browser
                            .find_element_by_class_name('js-cart-size').text)

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

    def test_confirm_order(self):
        """After filling the form we should be able to confirm an Order."""
        self.browser.find_element_by_id('id_payment_type_0').click()
        add_one_more = self.browser.find_element_by_xpath(self.add_product)
        add_one_more.click()  # perform some operations on cart
        wait()
        self.fill_and_submit_form()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order-success', ))
        )

    def fill_and_submit_form(self):
        self.browser.find_element_by_id('id_name').send_keys('Name')
        self.browser.find_element_by_id('id_city').send_keys('Санкт-Петербург')
        self.browser.find_element_by_id('id_phone').send_keys('22222222222')
        self.browser.find_element_by_id('id_email').send_keys('test@test.test')
        wait()
        submit = 'btn-send-se'
        self.browser.find_element_by_id(submit).click()
        wait()


class SitePage(SeleniumTestCase):

    def setUp(self):
        self.page_top = FlatPage.objects.create(
            title='Navigation',
            slug='navi',
        )
        self.page_last = FlatPage.objects.create(
            title='Contacts',
            slug='contacts',
            parent=self.page_top
        )
        self.browser.get(self.live_server_url + self.page_last.get_absolute_url())
        self.browser.execute_script('localStorage.clear();')
        self.browser.get(self.live_server_url + self.page_last.get_absolute_url())
        wait()

    @property
    def accordion_title(self):
        return self.browser.find_element_by_id(
            'js-accordion-title-{}'.format(self.page_top.id))

    @property
    def accordion_content(self):
        return self.browser.find_element_by_id(
            'js-accordion-content-{}'.format(self.page_top.id))

    def test_accordion_minimized(self):
        """Accordion item should be minimized by default"""
        self.assertFalse(self.accordion_content.is_displayed())

    def test_accordion_expand(self):
        """Accordion item should expand by click on title"""
        accordion_title = self.accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        wait()

        self.assertTrue(accordion_content.is_displayed())

    def test_accordion_minimize_by_double_click(self):
        """Accordion item should be minimized by two clicks on title"""
        accordion_title = self.accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        wait()
        accordion_title.click()
        wait()

        self.assertFalse(accordion_content.is_displayed())


@override_settings(DEBUG=True)
class YandexMetrika(SeleniumTestCase):

    def setUp(self):
        """
        We should use self.browser.get(...) in this case, because we
        faced a problems with it in setUpClass.
        """
        server = self.live_server_url
        product_id = Product.objects.first().id
        self.product_page = server + reverse('product', args=(product_id,))
        self.category_page = server + reverse(
            'category', args=(Category.objects.first().page.slug,))
        self.browser.get(self.live_server_url)

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
        self.browser.find_element_by_id('btn-to-basket').click()
        wait()

    def go_to_cart(self):
        self.browser.find_element_by_class_name('js-go-to-cart').click()
        wait()

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
        self.browser.find_element_by_class_name('js-browse-product').click()

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
        self.browser.find_element_by_class_name('js-cart-remove').click()
        wait()

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
        self.buy_product()
        self.go_to_cart()
        self.prevent_default('submit', '#order-form-full')
        self.browser.find_element_by_id('id_phone').send_keys('22222222222')
        self.browser.find_element_by_id('id_email').send_keys('test@test.ru')
        self.browser.find_element_by_id('order-form-full').submit()

        self.assertTrue('FULL_BUY_SEND' in self.reached_goals)
        self.assertTrue('CMN_BUY_SEND' in self.reached_goals)

    def test_cart_open(self):
        """User navigates to Cart."""
        self.buy_product()
        self.prevent_default('click', '.js-go-to-cart')
        self.go_to_cart()
        wait()
        self.assertTrue('CART_OPEN' in self.reached_goals)

        self.prevent_default('click', '.btn-to-order')
        show_cart_dropdown(self.browser)
        self.browser.find_element_by_class_name('btn-to-order').click()
        self.assertTrue('CART_OPEN' in self.reached_goals)

    def test_select_phone(self):
        """User selects site phone number."""
        self.select_text('js-copy-phone')
        self.browser.find_element_by_class_name('js-copy-phone').click()

        self.assertTrue('COPY_PHONE' in self.reached_goals)

    def test_select_email(self):
        """User selects site email."""
        self.prevent_default('click', '.js-copy-mail')
        self.select_text('js-copy-mail')
        self.browser.find_element_by_class_name('js-copy-mail').click()

        self.assertTrue('COPY_MAIL' in self.reached_goals)


class Search(SeleniumTestCase):

    QUERY = 'Cate'

    def setUp(self):
        """
        We should use self.browser.get(...) in this case, because we
        faced a problems with it in setUpClass.
        """
        self.browser.get(self.live_server_url)
        wait()

    @property
    def autocomplete(self):
        return self.browser.find_element_by_class_name('autocomplete-suggestions')

    @property
    def input(self):
        return self.browser.find_element_by_class_name('js-search-input')

    def fill_input(self):
        """Enter correct search term."""
        self.input.send_keys(self.QUERY)
        wait()

    def clear_input(self):
        """Enter correct search term."""
        self.input.send_keys(Keys.BACKSPACE*len(self.QUERY))
        wait()

    def test_autocomplete_can_expand_and_collapse(self):
        """
        Autocomplete should minimize during user typing correct search query.
        Autocomplete should minimize by removing search query.
        """
        wait()
        self.fill_input()
        # fill input and autocomplete expands
        self.assertTrue(self.autocomplete.is_displayed())

        # remove search term ...
        self.input.send_keys(Keys.BACKSPACE * len(self.QUERY))
        wait()
        # ... and autocomplete collapse
        self.assertFalse(self.autocomplete.is_displayed())
        self.clear_input()

    def test_autocomplete_item_link(self):
        """First autocomplete item should link on category page by click."""
        self.fill_input()
        first_item = self.autocomplete.find_element_by_css_selector(
            ':first-child')
        wait()
        first_item.click()
        wait()

        self.assertTrue('/catalog/categories/' in self.browser.current_url)
        self.clear_input()

    def test_autocomplete_see_all_item(self):
        """
        Autocomplete should contain "see all" item.
        `See all` item links on search results page.
        """
        self.fill_input()
        last_item = self.autocomplete.find_element_by_class_name(
            'autocomplete-last-item')
        last_item.click()
        wait()

        self.assertTrue('/search/' in self.browser.current_url)
        self.clear_input()

    def test_search_have_results(self):
        """Search results page should contain links on relevant pages."""
        self.fill_input()
        search_form = self.browser.find_element_by_class_name('search-form')
        search_form.submit()
        wait()
        self.assertTrue(self.browser.find_element_by_link_text(
            'Category #0 of #Category #0 of #Category #0'))

        self.assertTrue(self.browser.find_element_by_link_text(
            'Category #0'))
        self.clear_input()

    def test_search_results_empty(self):
        """Search results for wrong term should contain empty result set."""
        self.input.send_keys('Not existing search query')
        button_submit = self.browser.find_element_by_id('search-submit')
        button_submit.click()
        wait()
        h1 = self.browser.find_element_by_tag_name('h1')

        self.assertTrue(h1.text == 'По вашему запросу ничего не найдено')
        self.clear_input()
