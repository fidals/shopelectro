"""
Selenium-based tests.

If you need to create new test-suite, subclass it from SeleniumTestCase class.
Every Selenium-based test suite uses fixture called dump.json.
"""

import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from seleniumrequests import Remote  # We use this instead of standard selenium
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from django.core import mail
from django.conf import settings
from django.db.models import Count
from django.test import LiveServerTestCase, override_settings
from django.urls import reverse

from pages.models import FlatPage, CustomPage, Page

from shopelectro.models import Category, Product
from shopelectro.tests.helpers import disable_celery


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


def add_to_cart(browser, live_server_url):
    browser.get(live_server_url + Product.objects.first().url)
    browser.find_element_by_class_name('btn-to-basket').click()
    wait()


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super(SeleniumTestCase, cls).setUpClass()
        cls.browser = Remote(
            command_executor='http://se-selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME
        )
        cls.browser.implicitly_wait(10)
        cls.browser.set_window_size(1920, 1080)

    @classmethod
    def tearDownClass(cls):
        """Close selenium session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()


@disable_celery
@override_settings(DEBUG=True, INTERNAL_IPS=tuple())
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

    @disable_celery
    def test_order_backcall_email(self):
        """Back call phone number should be same in sent email"""
        self.browser.find_element_by_class_name('js-backcall-order').click()
        self.browser.find_element_by_id('back-call-phone').send_keys('2222222222')
        self.browser.find_element_by_class_name('js-send-backcall').click()
        wait(3)
        sent_mail = mail.outbox[0]

        self.assertEqual(sent_mail.subject, settings.EMAIL_SUBJECTS['call'])
        self.assertIn('+7 (222) 222 22 22', sent_mail.body)

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
        add_to_cart(self.browser, self.live_server_url)

        show_cart_dropdown(self.browser)
        self.browser.find_element_by_class_name('basket-reset').click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name('js-cart-is-empty')

        self.assertTrue(cart_is_empty.is_displayed())

    def test_product_total_price_in_dropdown(self):
        add_to_cart(self.browser, self.live_server_url)

        product_price = int(Product.objects.first().price)
        show_cart_dropdown(self.browser)
        product_total_price = self.browser.find_element_by_class_name('js-basket-sum').text
        product_total_price_price_in_cart = int(product_total_price.split(' ')[0])
        wait()
        self.assertTrue(product_price == product_total_price_price_in_cart)


class CategoryPage(SeleniumTestCase):

    PRODUCTS_TO_LOAD = 48

    def setUp(self):
        self.browser.delete_all_cookies()
        server = self.live_server_url
        self.testing_url = lambda slug: server + reverse('category', args=(slug,))

        root_category = Category.objects.filter(parent=None).first()
        children_category = Category.objects.filter(parent=root_category).first()
        category_with_product_less_then_LOAD_LIMIT = Category.objects.annotate(
            prod_count=Count('products')).exclude(prod_count=0).filter(
            prod_count__lt=self.PRODUCTS_TO_LOAD).first()

        self.root_category = self.testing_url(root_category.page.slug)
        self.children_category = self.testing_url(children_category.page.slug)
        self.deep_children_category = self.testing_url(
            category_with_product_less_then_LOAD_LIMIT.page.slug)
        self.apply_btn = 'js-apply-filter'
        self.filter_tag = 'label[for="tag-6-v"]'

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

    def test_loaded_products_count(self):
        """Any CategoryPage should contain predefined products count by default."""
        self.browser.get(self.root_category)
        loaded_products = self.browser.find_element_by_class_name(
            'js-products-showed-count').text
        self.assertEqual(self.PRODUCTS_TO_LOAD, int(loaded_products))

    def test_load_more_products(self):
        """
        We can load another set of products by clicking load more button.

        After that we wait some time for XHR will be performed
        and there will be new count of loaded products.
        """
        self.browser.get(self.root_category)
        self.browser.refresh()
        self.load_more_button.click()  # Let's load another set of products.
        wait()
        loaded_products_count = self.browser.find_element_by_class_name(
            'js-products-showed-count').text

        self.assertEqual(2 * self.PRODUCTS_TO_LOAD, int(loaded_products_count))

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
        """Sorting should be by cheapest by default."""
        self.browser.get(self.children_category)
        cheapest_sort_option = self.browser.find_element_by_css_selector(
            '.selectpicker option:checked'
        )

        self.assertTrue(cheapest_sort_option.is_selected())

    def test_change_sorting(self):
        """We able to change sorting option."""
        self.browser.get(self.children_category)
        expensive_sort_option = self.browser.find_elements_by_css_selector(
            '.selectpicker option'
        )[1]

        expensive_sort_option.click()
        expensive_sort_option = self.browser.find_element_by_css_selector(
            '.selectpicker option:checked'
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
        self.load_more_button.click()  # Let's load another PRODUCTS_TO_LOAD products.
        wait(15)
        recently_loaded_product = self.browser.find_elements_by_class_name(
            'js-product-to-cart')[self.PRODUCTS_TO_LOAD + 1]
        recently_loaded_product.click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name(
            'js-cart-is-empty')

        self.assertFalse(cart_is_empty.is_displayed())

    def test_apply_filter_state(self):
        """Apply filters btn should be disabled with no checked tags."""
        self.browser.get(self.root_category)

        attribute = self.browser.find_element_by_class_name(self.apply_btn).get_attribute('disabled')
        self.assertTrue(attribute, True)

        self.browser.find_element_by_css_selector(self.filter_tag).click()
        attribute = self.browser.find_element_by_class_name(self.apply_btn).get_attribute('disabled')
        self.assertEqual(attribute, None)

    def test_filter_products_by_tag(self):
        """Products should be filterable by tag."""
        total_class = 'js-total-products'
        self.browser.get(self.root_category)

        before_products_count = self.browser.find_element_by_class_name(total_class).text
        self.browser.find_element_by_css_selector(self.filter_tag).click()
        self.browser.find_element_by_class_name(self.apply_btn).click()
        after_products_count = self.browser.find_element_by_class_name(total_class).text
        self.assertTrue(int(before_products_count) > int(after_products_count))

        self.browser.find_element_by_class_name('js-clear-tag-filter').click()
        after_products_count = self.browser.find_element_by_class_name(total_class).text
        self.assertTrue(int(before_products_count) == int(after_products_count))

    def test_filter_toggle_sections(self):
        """Filter sections should be toggleable."""
        self.browser.get(self.root_category)

        section_toggler = self.browser.find_element_by_class_name('js-toggle-tag-group')
        self.assertNotIn('opened', section_toggler.get_attribute('class'))

        section_toggler.click()
        self.assertIn('opened', section_toggler.get_attribute('class'))

    def test_filter_and_sorting(self):
        """Sorting should work after filtering."""
        self.browser.get(self.root_category)

        self.browser.find_element_by_css_selector(self.filter_tag).click()
        self.browser.find_element_by_class_name(self.apply_btn).click()
        product_card = self.browser.find_element_by_class_name('product-card')
        old_price = product_card.find_element_by_class_name('product-card-price').text

        expensive_sort_option = self.browser.find_elements_by_css_selector(
            '.selectpicker option'
        )[1]
        expensive_sort_option.click()
        product_card = self.browser.find_element_by_class_name('product-card')
        new_price = product_card.find_element_by_class_name('product-card-price').text

        self.assertTrue(old_price < new_price)

    def test_load_more_after_filtering(self):
        """Sorting should work after filtering."""
        self.browser.get(self.root_category)
        wait()

        self.browser.find_element_by_css_selector(self.filter_tag).click()
        self.browser.find_element_by_class_name(self.apply_btn).click()

        self.load_more_button.click()
        wait()
        new_product_cards = len(self.browser.find_elements_by_class_name('product-card'))

        self.assertEqual(new_product_cards, 50)


class ProductPage(SeleniumTestCase):

    PRODUCT_ID = 1

    def setUp(self):
        """Set up testing url and dispatch selenium webdriver."""
        self.product = Product.objects.get(id=self.PRODUCT_ID)
        server = self.live_server_url
        self.test_product_page = server + self.product.url
        self.success_order = server + reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order-success',))
        self.product_name = self.product.name
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

        # click on second image preview
        image_preview = self.browser.find_elements_by_class_name('js-image-switch')[1]
        image_preview.click()
        wait()
        switched_path = get_main_image_src()

        self.assertNotEquals(not_switched_path, switched_path)

    def test_one_click_buy_disabled_with_empty_phone(self):
        """By default .btn-one-click-order should be disabled"""
        self.browser.find_element_by_id(
            'input-one-click-phone').send_keys(Keys.BACKSPACE)

        self.assertTrue(self.one_click.get_attribute('disabled'))

    @disable_celery
    def test_one_click_buy_action(self):
        """We can order product via one-click buy button."""
        self.browser.find_element_by_id(
            'input-one-click-phone').send_keys('2222222222')
        self.one_click.click()
        wait()

        self.assertEqual(self.browser.current_url, self.success_order)

    @disable_celery
    def test_one_click_buy_order_email(self):
        product_vendor_code = self.product.vendor_code

        increase_quantity = self.browser.find_element_by_xpath(
            '//*[@class="product-price-wrapper"]/div[1]/div[1]/span[3]/button[1]'
        )
        increase_quantity.click()
        increase_quantity.click()
        result_quantity = int(
            self.browser.find_element_by_class_name('js-touchspin')
            .get_attribute('value')
        )
        self.browser.execute_script('$("#input-one-click-phone").val("");')
        (self.browser
            .find_element_by_id('input-one-click-phone')
            .send_keys('2222222222')
        )
        self.one_click.click()
        wait(3)

        sent_mail_body = mail.outbox[0].body
        self.assertIn('+7 (222) 222 22 22', sent_mail_body)
        self.assertInHTML(
            '<td align="left"' +
            'style="border-bottom:1px solid #e4e4e4;padding:10px">{0}</td>'
            .format(product_vendor_code),
            sent_mail_body)
        self.assertIn(self.product.url, sent_mail_body)
        self.assertIn('{0} шт.'.format(result_quantity), sent_mail_body)
        self.assertInHTML(
            '<td align="right" style="padding:5px 10px">{0} руб.</td>'
            .format(int(self.product.price * result_quantity)),
            sent_mail_body
        )

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

    def test_new_fivestar_feedback(self):
        text_of_feedback = 'Five star rating.'

        # create new feedback
        self.browser.find_element_by_css_selector('.js-open-feedback-modal').click()
        feedback_modal = self.browser.find_element_by_id('product-feedback-modal')
        form_fields = feedback_modal.find_elements_by_class_name('form-control')

        for form_field in form_fields:
            form_field.send_keys(text_of_feedback)

        rating_stars = self.browser.find_element_by_class_name('js-rating')
        rating_stars.find_element_by_css_selector('.rating-icon-empty:last-child').click()
        feedback_modal.find_element_by_css_selector('.js-send-feedback').click()
        wait()

        # check for new feedback on page with `text_of_feedback`
        self.browser.refresh()
        feedback_list = self.browser.find_element_by_id('feedback-list')
        text = feedback_list.find_element_by_class_name('feedback-block-content').text

        self.assertIn(text_of_feedback, text)

    def test_feedback_filter(self):
        stars = self.browser.find_elements_by_class_name('js-filter-trigger')

        for star in stars:
            star.click()

        wait()
        feedback_list = self.browser.find_element_by_id('feedback-list')
        feedback = feedback_list.find_elements_by_class_name('feedback-block-content')

        self.assertTrue(all(not element.is_displayed() for element in feedback))


@disable_celery
class OrderPage(SeleniumTestCase):

    @staticmethod
    def get_cell(pos, col):
        # table columns mapping: http://prntscr.com/bsv5hp
        cols = {
            'id': 1,
            'name': 3,
            'count': 4,
            'price': 5,
            'remove': 6,
        }
        product_row = '//*[@id="js-order-list"]/div[2]/div[{pos}]/div[{col}]'

        return product_row.format(pos=pos, col=cols[col])

    def setUp(self):
        self.browser.delete_all_cookies()
        self.order_page = CustomPage.objects.get(slug='order')
        self.cart_dropdown = 'basket-parent'
        self.first_product_id = '405'
        self.remove_product = self.get_cell(pos=4, col='remove') + '/div'
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
                        self.browser.find_element_by_class_name('js-order-contain').text)

    def test_table_and_dropdown_are_synchronized(self):
        def get_counts():
            table_count_ = (
                self.browser.find_element_by_id('cart-page-prods-count').text
            )

            header_count = (
                self.browser.find_element_by_class_name('js-cart-size').text
            )

            return table_count_, header_count

        self.browser.refresh()
        table_count, dropdown_count = get_counts()
        self.assertIn('5', table_count)
        self.assertIn('5', dropdown_count)
        self.browser.find_element_by_xpath(
            self.add_product.format(self.first_product_id)).click()
        wait()

        table_count, dropdown_count = get_counts()
        self.assertIn('6', table_count)
        self.assertIn('6', dropdown_count)
        wait()

        self.browser.find_element_by_xpath(
            self.remove_product.format(self.first_product_id)).click()
        wait()

        table_count, dropdown_count = get_counts()
        self.assertIn('4', dropdown_count)
        self.assertIn('4', table_count)

    def test_confirm_order(self):
        """After filling the form we should be able to confirm an Order."""
        self.perform_operations_on_cart()
        self.fill_and_submit_form()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order-success', ))
        )

    def perform_operations_on_cart(self):
        self.browser.find_element_by_id('id_payment_type_0').click()
        add_one_more = self.browser.find_element_by_xpath(self.add_product)
        add_one_more.click()
        wait()

    def fill_and_submit_form(self):
        self.browser.execute_script('$("#id_name").val("");')
        self.browser.execute_script('$("#id_city").val("");')
        self.browser.execute_script('$("#id_phone").val("");')
        self.browser.execute_script('$("#id_email").val("");')

        self.browser.find_element_by_id('id_name').send_keys('Name')
        self.browser.find_element_by_id('id_city').send_keys('Санкт-Петербург')
        self.browser.find_element_by_id('id_phone').send_keys('2222222222')
        self.browser.find_element_by_id('id_email').send_keys('test@test.test')
        wait()
        self.browser.find_element_by_id('submit-order').click()
        wait()

    @disable_celery
    def test_order_email(self):
        codes = self.browser.find_elements_by_class_name(
            'order-table-product-id')
        clean_codes = []
        for code in codes:
            clean_codes.append(code.text)

        self.perform_operations_on_cart()
        final_price = self.browser.find_element_by_id('cart-page-sum').text[:-5]

        self.fill_and_submit_form()
        wait(3)
        sent_mail_body = mail.outbox[0].body

        self.assertIn('Наличные', sent_mail_body)
        self.assertIn('+7 (222) 222 22 22', sent_mail_body)
        self.assertIn('test@test.test', sent_mail_body)
        self.assertInHTML(
            '<strong style="font-weight:bold">Санкт-Петербург</strong>',
            sent_mail_body
        )
        for code in clean_codes:
            self.assertInHTML(
                '<td align="left"' +
                'style="border-bottom:1px solid #e4e4e4;padding:10px">{0}</td>'
                .format(code),
                sent_mail_body
            )
            self.assertIn(
                '<a href="https://www.shopelectro.ru{0}"'
                .format(reverse('product', args=(code,))),
                sent_mail_body
            )

        self.assertInHTML(
            '<td align="right" style="padding:5px 10px">{0} руб.</td>'
            .format(final_price),
            sent_mail_body
        )


class SitePage(SeleniumTestCase):

    def setUp(self):
        self.page_top = FlatPage.objects.create(
            name='Navigation',
            slug='navi',
        )
        self.page_last = FlatPage.objects.create(
            name='Contacts',
            slug='contacts',
            parent=self.page_top
        )

        self.browser.get(self.live_server_url + self.page_last.url)
        self.browser.execute_script('localStorage.clear();')
        self.browser.get(self.live_server_url + self.page_last.url)

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


@disable_celery
@override_settings(DEBUG=True, INTERNAL_IPS=tuple())
class YandexMetrika(SeleniumTestCase):

    def setUp(self):
        """
        We should use self.browser.get(...) in this case, because we
        faced a problems with it in setUpClass.
        """
        server = self.live_server_url
        product_vendor_code = Product.objects.first().vendor_code
        self.product_page = server + reverse('product', args=(product_vendor_code,))
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

    def test_autocomplete_by_vendor_code(self):
        """Autocomplete should work by product's vendor code."""
        product_vendor_code = Product.objects.first().vendor_code

        self.input.send_keys(product_vendor_code)
        first_item = self.autocomplete.find_element_by_css_selector(':first-child')
        first_item.click()
        wait()

        test_vendor_code = self.browser.find_element_by_class_name('product-article').text

        self.assertIn(str(product_vendor_code), test_vendor_code)

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
