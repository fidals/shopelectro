"""
Selenium-based tests.

If you need to create new test-suite, subclass it from helpers.SeleniumTestCase class.
Every Selenium-based test suite uses fixture called dump.json.
"""
import unittest

from django.conf import settings
from django.core import mail
from django.db.models import Count
from django.test import override_settings
from django.urls import reverse  # Ignore CPDBear
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC, ui

from pages.models import FlatPage, CustomPage, Page

from shopelectro.models import Category, Product
from shopelectro.tests import helpers


def make_backcall(browser):
    """Trigger backcall modal. Fill it and submit."""
    wait = ui.WebDriverWait(browser, 60)
    browser.find_element_by_class_name('js-backcall-order').click()
    wait.until(EC.visibility_of_element_located(
        (By.ID, 'back-call-modal-label')
    ))
    browser.find_element_by_id('back-call-phone').send_keys('2222222222')
    browser.find_element_by_xpath(
        '//*[@id="back-call-time"]/option[3]').click()
    browser.find_element_by_class_name('js-send-backcall').click()
    wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, 'js-backcall-success')
    ))


def show_cart_dropdown(browser):
    wait = ui.WebDriverWait(browser, 60)
    cart_parent = browser.find_element_by_class_name('basket-parent')
    helpers.hover(browser, cart_parent)
    wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, 'js-cart-wrapper')
    ))


def add_to_cart(browser, live_server_url):
    browser.get(live_server_url + Product.objects.first().url)
    browser.find_element_by_class_name('btn-to-basket').click()


@helpers.try_again_on_stale_element(3)
def is_cart_empty(browser):
    show_cart_dropdown(browser)
    return browser.find_element_by_class_name('js-cart-is-empty').is_displayed()


def wait_page_loading(browser):
    ui.WebDriverWait(browser, 60).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, 'content')
        )
    )


@helpers.disable_celery
@override_settings(DEBUG=True, INTERNAL_IPS=tuple())
class Header(helpers.SeleniumTestCase):

    def setUp(self):
        """Set up testing urls and dispatch selenium webdriver."""
        self.browser.get(self.live_server_url)
        wait_page_loading(self.browser)

    def test_call_modal_not_visible(self):
        """By default we shouldn't see call modal."""
        modal = self.browser.find_element_by_id('back-call-modal')
        self.assertFalse(modal.is_displayed())

    def test_order_backcall(self):
        """After filling modal fields user can successfully order backcall."""
        make_backcall(self.browser)
        self.assertTrue(
            self.browser
            .find_element_by_class_name('js-backcall-success')
            .is_displayed()
        )

    @helpers.disable_celery
    def test_order_backcall_email(self):
        """Back call phone number should be same in sent email."""
        make_backcall(self.browser)
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, settings.EMAIL_SUBJECTS['call'])
        self.assertIn('+7 (222) 222 22 22', sent_mail.body)

    def test_empty_cart(self):
        """By default there should be 'Корзина пуста' in the header's cart."""
        cart_in_header = self.browser.find_element_by_class_name('js-header-cart')

        self.assertTrue('Корзина пуста' in cart_in_header.text)

    def test_cart_hover(self):
        """Cart dropdown should be visible on hover."""
        cart = self.browser.find_element_by_class_name('basket-wrapper')
        show_cart_dropdown(self.browser)

        self.assertTrue(cart.is_displayed())

    def test_cart_flush(self):
        """We can flush cart from header's cart dropdown."""
        add_to_cart(self.browser, self.live_server_url)
        show_cart_dropdown(self.browser)
        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'basket-reset')
        )).click()
        self.wait.until_not(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'basket-wrapper')
        ))

        self.assertTrue(is_cart_empty(self.browser))

    def test_product_total_price_in_dropdown(self):
        add_to_cart(self.browser, self.live_server_url)
        product_price = int(Product.objects.first().price)
        show_cart_dropdown(self.browser)
        product_total_price = self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'js-basket-sum'))
        ).text
        product_total_price_in_cart = int(product_total_price.split(' ')[0])

        self.assertTrue(product_price == product_total_price_in_cart)


class CategoryPage(helpers.SeleniumTestCase):

    PRODUCTS_TO_LOAD = 48

    def setUp(self):
        def get_testing_url(slug):
            return self.live_server_url + reverse('category', args=(slug,))
        self.browser.delete_all_cookies()

        root_category = Category.objects.filter(parent=None).first()
        children_category = Category.objects.filter(parent=root_category).first()
        category_with_product_less_then_LOAD_LIMIT = (
            Category.objects
            .annotate(prod_count=Count('products'))
            .exclude(prod_count=0)
            .filter(prod_count__lt=self.PRODUCTS_TO_LOAD)
            .first()
        )

        self.root_category = get_testing_url(root_category.page.slug)
        self.children_category = get_testing_url(children_category.page.slug)
        self.deep_children_category = get_testing_url(
            category_with_product_less_then_LOAD_LIMIT.page.slug
        )

        self.apply_btn = 'js-apply-filter'
        self.filter_tag = 'label[for="tag-24-v"]'

    @property
    def product_card(self):
        return self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'product-card')
        ))

    def wait_page_loading(self):
        wait_page_loading(self.browser)

    @property
    def load_more_button(self):
        return self.wait.until(EC.presence_of_element_located(
            (By.ID, 'btn-load-products')
        ))

    def load_more_products(self):
        self.load_more_button.click()
        self.wait.until_not(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'js-products-showed-count'),
                str(self.PRODUCTS_TO_LOAD)
            )
        )

    @property
    def is_empty_cart(self):
        return is_cart_empty(self.browser)

    def test_breadcrumbs(self):
        """
        Test breadcrumbs.

        Breadcrumbs should be presented on every category page.
        Their count depends on category's depth in a catalog tree.
        For the root categories, for example, there should be 3 crumbs.
        """
        # There should be three crumbs in 'root category'.
        self.browser.get(self.root_category)
        self.wait_page_loading()
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')

        self.assertEqual(len(crumbs), 3)

        # In 'deep category' there should be more crumbs
        self.browser.get(self.children_category)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')

        self.assertEqual(len(crumbs), 4)

    def test_loaded_products_count(self):
        """Any CategoryPage should contain predefined products count by default."""
        self.browser.get(self.root_category)
        self.wait_page_loading()
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
        self.wait_page_loading()
        # self.browser.refresh()
        self.load_more_products()  # Let's load another set of products.
        loaded_products_count = self.browser.find_element_by_class_name(
            'js-products-showed-count'
        ).text

        self.assertEqual(2 * self.PRODUCTS_TO_LOAD, int(loaded_products_count))

    def test_load_more_hidden_in_fully_loaded_categories(self):
        """If category has less products than LOAD_LIMIT we shouldn't see `Load more` button."""
        self.browser.get(self.deep_children_category)
        self.wait_page_loading()
        self.assertTrue('hidden' in self.load_more_button.get_attribute('class'))

    def test_default_view_is_tile(self):
        """
        By default, category page should has tile view.

        It means, after rendering a page,
        tile view selector should has 'active' class
        and category wrapper 'view-mode-tile' class.
        """
        self.browser.get(self.children_category)
        self.wait_page_loading()
        tile_view_selector = self.browser.find_element_by_class_name(
            'js-icon-mode-tile')
        products_view = self.browser.find_element_by_id('category-right')

        self.assertTrue('active' in tile_view_selector.get_attribute('class'))
        self.assertTrue('view-mode-tile' in products_view.get_attribute('class'))

    def test_change_view(self):
        """We should be able to change default view to list view without reloading a page."""
        self.browser.get(self.children_category)
        self.wait_page_loading()
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
        self.wait_page_loading()
        cheapest_sort_option = self.browser.find_element_by_css_selector(
            '.selectpicker option:checked'
        )

        self.assertTrue(cheapest_sort_option.is_selected())

    def test_change_sorting(self):
        """We able to change sorting option."""
        self.browser.get(self.children_category)
        self.wait_page_loading()
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
        self.wait_page_loading()
        self.browser.find_elements_by_class_name(
            'js-product-to-cart')[0].click()
        self.assertFalse(self.is_empty_cart)

    def test_add_to_cart_after_load_more(self):
        self.browser.get(self.root_category)
        self.wait_page_loading()
        # Let's load another PRODUCTS_TO_LOAD products.
        self.load_more_products()
        recently_loaded_product = self.browser.find_elements_by_class_name(
            'js-product-to-cart'
        )[self.PRODUCTS_TO_LOAD + 1]
        recently_loaded_product.click()
        self.assertFalse(self.is_empty_cart)

    def test_apply_filter_state(self):
        """Apply filters btn should be disabled with no checked tags."""
        self.browser.get(self.root_category)
        self.wait_page_loading()

        attribute = self.browser.find_element_by_class_name(
            self.apply_btn).get_attribute('disabled')
        self.assertTrue(attribute, True)

        self.browser.find_element_by_css_selector(self.filter_tag).click()
        attribute = self.browser.find_element_by_class_name(
            self.apply_btn).get_attribute('disabled')
        self.assertEqual(attribute, None)

    def test_filter_products_by_tag(self):
        total_class = 'js-total-products'
        self.browser.get(self.root_category)
        self.wait_page_loading()

        before_products_count = self.browser.find_element_by_class_name(total_class).text
        self.browser.find_element_by_css_selector(self.filter_tag).click()
        old_url = self.browser.current_url
        self.browser.find_element_by_class_name(self.apply_btn).click()
        self.wait.until(EC.url_changes(old_url))
        self.wait_page_loading()

        after_products_count = self.browser.find_element_by_class_name(total_class).text
        self.assertTrue(int(before_products_count) > int(after_products_count))

        self.browser.find_element_by_class_name('js-clear-tag-filter').click()
        after_products_count = self.browser.find_element_by_class_name(total_class).text
        self.assertTrue(int(before_products_count) == int(after_products_count))

    def test_filter_toggle_sections(self):
        """Filter sections should be toggleable."""
        self.browser.get(self.root_category)
        self.wait_page_loading()

        section_toggler = self.browser.find_element_by_class_name('js-toggle-tag-group')
        self.assertNotIn('opened', section_toggler.get_attribute('class'))

        section_toggler.click()
        self.assertIn('opened', section_toggler.get_attribute('class'))

    def test_filter_and_sorting(self):
        """Sorting should work after filtering."""
        self.browser.get(self.root_category)
        self.wait_page_loading()

        self.browser.find_element_by_css_selector(self.filter_tag).click()
        self.browser.find_element_by_class_name(self.apply_btn).click()
        old_price = self.product_card.find_element_by_class_name(
            'product-card-price'
        ).text

        expensive_sort_option = self.browser.find_elements_by_css_selector(
            '.selectpicker option'
        )[1]
        expensive_sort_option.click()
        new_price = self.product_card.find_element_by_class_name(
            'product-card-price'
        ).text

        self.assertTrue(old_price < new_price)

    def test_load_more_after_filtering(self):
        """Sorting should work after filtering."""
        self.browser.get(self.root_category)
        self.wait_page_loading()

        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'js-toggle-tag-group')
        )).click()

        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, self.filter_tag)
        )).click()
        self.browser.find_element_by_class_name(self.apply_btn).click()

        self.load_more_products()
        new_product_cards = len(self.browser.find_elements_by_class_name('product-card'))

        self.assertEqual(new_product_cards, 50)


class ProductPage(helpers.SeleniumTestCase):

    PRODUCT_ID = 1

    def setUp(self):
        """Set up testing url and dispatch selenium webdriver."""
        self.browser.delete_all_cookies()
        self.product = Product.objects.get(id=self.PRODUCT_ID)
        server = self.live_server_url
        self.test_product_page = server + self.product.url
        self.success_order = server + reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order-success',))
        self.product_name = self.product.name
        self.browser.get(self.test_product_page)
        wait_page_loading(self.browser)
        self.one_click = self.browser.find_element_by_id('btn-one-click-order')

    def test_breadcrumbs(self):
        """
        Test breadcrumb properties.

        Breadcrumbs should be presented on every product page.
        Their count depends on product's depth in a catalog tree.
        """
        # There should be 6 items in breadcrumbs for this case
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 6)

    def test_ui_elements(self):
        """
        Test ProductPage ui.

        Every ProductPage should have button to make order and input
        for phone number.
        """
        button_order = self.browser.find_element_by_id('btn-to-basket')
        input_one_click_order = self.browser.find_element_by_id(
            'input-one-click-phone')

        self.assertTrue(button_order)
        self.assertTrue(self.one_click)
        self.assertTrue(input_one_click_order)

    def test_fancybox(self):  # Ignore PyDocStyleBear
        """ProductPage should have fancyBox plugin."""
        self.browser.find_element_by_id('product-image-big').click()
        fancybox_wrap = self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'fancybox-wrap')
        ))

        self.assertTrue(fancybox_wrap)

    def test_images_switch(self):
        """If product has > 1 image, we could to switch them by clicking."""
        def get_main_image_src():
            image = self.browser.find_element_by_id('product-image-big')
            return image.get_attribute('src')
        not_switched_src = get_main_image_src()

        def wait_switched_src(browser):
            src = (
                browser
                .find_element_by_id('product-image-big')
                .get_attribute('src')
            )
            return src if src != not_switched_src else False

        # click on second image preview
        image_preview = self.browser.find_elements_by_class_name('js-image-switch')[1]
        image_preview.click()
        switched_src = self.wait.until(wait_switched_src)
        switched_src = get_main_image_src()

        self.assertNotEquals(not_switched_src, switched_src)

    def test_one_click_buy_disabled_with_empty_phone(self):
        """By default .btn-one-click-order should be disabled."""
        (
            self.browser
            .find_element_by_id('input-one-click-phone')
            .send_keys(Keys.BACKSPACE)
        )

        self.assertTrue(self.one_click.get_attribute('disabled'))

    @helpers.disable_celery
    def test_one_click_buy_action(self):
        """We can order product via one-click buy button."""
        self.browser.find_element_by_id(
            'input-one-click-phone').send_keys('2222222222')
        self.one_click.click()
        self.wait.until(EC.url_to_be(self.success_order))

        self.assertEqual(self.browser.current_url, self.success_order)

    @helpers.disable_celery
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
        phone_field = self.browser.find_element_by_id('input-one-click-phone')
        phone_field.send_keys('2222222222')
        self.one_click.click()
        self.wait.until(EC.url_to_be(self.success_order))

        sent_mail_body = mail.outbox[0].body
        self.assertIn('+7 (222) 222 22 22', sent_mail_body)
        self.assertInHTML(
            '<td align="left"'
            'style="border-bottom:1px solid #E4E4E4;padding:10px">{0}</td>'
            .format(product_vendor_code),
            sent_mail_body
        )
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
        self.assertFalse(is_cart_empty(self.browser))

    def test_product_name_in_cart_dropdown(self):
        self.browser.find_element_by_class_name('btn-to-basket').click()
        show_cart_dropdown(self.browser)
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        cart = cart_parent.find_element_by_class_name('basket-wrapper')

        self.assertTrue(self.product_name in cart.text)

    def test_actual_product_count_in_cart_dropdown(self):
        def get_cart_size_el():
            return self.browser.find_element_by_class_name('js-cart-size')

        cart_size = get_cart_size_el().text
        self.browser.find_element_by_id('product-count').send_keys('42')
        self.browser.find_element_by_class_name('btn-to-basket').click()
        self.wait.until_not(EC.text_to_be_present_in_element(
            (By.CLASS_NAME, 'js-cart-size'), cart_size
        ))
        self.assertTrue('42' in get_cart_size_el().text)

    def test_new_fivestar_feedback(self):
        text_of_feedback = 'Five star rating.'

        # create new feedback
        condition_to_wait_modal = EC.visibility_of_element_located(
            (By.ID, 'feedback-modal-dignities')
        )
        self.browser.find_element_by_class_name('js-open-feedback-modal').click()
        self.wait.until(condition_to_wait_modal)
        feedback_modal = self.browser.find_element_by_id('product-feedback-modal')
        form_fields = feedback_modal.find_elements_by_class_name('form-control')

        for form_field in form_fields:
            form_field.send_keys(text_of_feedback)

        rating_stars = self.browser.find_element_by_class_name('js-rating')
        rating_stars.find_element_by_css_selector('.rating-icon-empty:last-child').click()
        feedback_modal.find_element_by_class_name('js-send-feedback').click()
        self.wait.until_not(condition_to_wait_modal)

        # check for new feedback on page with `text_of_feedback`
        self.browser.refresh()
        wait_page_loading(self.browser)
        feedback_list = self.browser.find_element_by_id('feedback-list')
        text = feedback_list.find_element_by_class_name('feedback-block-content').text

        self.assertIn(text_of_feedback, text)

    def test_feedback_filter(self):
        stars = self.browser.find_elements_by_class_name('js-filter-trigger')

        for star in stars:
            star.click()

        feedbacks = self.wait.until_not(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, '#feedback-list .feedback-block-content')
        ))
        self.assertTrue(feedbacks)


@helpers.disable_celery
class OrderPage(helpers.SeleniumTestCase):

    @staticmethod
    def get_cell(pos, col):
        # table columns mapping: http://prntscr.com/bsv5hp  # Ignore InvalidLinkBear
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
        self.success_order_url = '{}{}'.format(
            self.live_server_url,
            reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order-success',))
        )
        self.buy_products()
        self.wait.until_not(is_cart_empty)
        self.browser.get(self.live_server_url + self.order_page.url)
        wait_page_loading(self.browser)

    def tearDown(self):
        self.browser.execute_script('localStorage.clear();')

    def buy_products(self):
        self.browser.get(self.live_server_url + self.category)
        for i in range(1, 6):
            self.browser.find_element_by_xpath(
                '//*[@id="products-wrapper"]/div[{}]/div[2]/div[5]/button'
                .format(i)
            ).click()

    def perform_operations_on_cart(self):
        self.click((By.ID, 'id_payment_type_0'))
        add_one_more = self.click((By.XPATH, self.add_product))
        self.wait.until(EC.staleness_of(add_one_more))

    def fill_and_submit_form(self):
        @helpers.try_again_on_stale_element(3)
        def insert_value(id, keys, expected_keys=''):
            def expected_conditions(browser):
                return browser.find_element_by_id(id).get_attribute('value')
            self.send_keys_and_wait(keys, (By.ID, id), expected_keys=expected_keys)
            self.wait.until(expected_conditions)

        insert_value('id_name', 'Name')
        insert_value('id_city', 'Санкт-Петербург')
        insert_value('id_phone', '2222222222', expected_keys='+7 (222) 222 22 22')
        insert_value('id_email', 'test@test.test')
        self.click((By.ID, 'submit-order'))
        self.wait.until(EC.url_to_be(self.success_order_url))

    def test_table_is_presented_if_there_is_some_products(self):
        """If there are some products in cart, we should see them in table on OrderPage."""
        order_table = self.browser.find_element_by_class_name('order-list')
        self.assertTrue(order_table.is_displayed())

    def test_remove_product_from_table(self):
        """We can remove product from table and see the changes immediately."""
        remove_el = self.browser.find_element_by_xpath(self.remove_product)
        remove_el.click()
        self.wait.until(EC.staleness_of(remove_el))

        self.assertFalse(
            self.first_product_id in
            self.browser.find_element_by_class_name('order-list').text
        )

    def test_empty_cart(self):
        """After removing every product from cart we should see that it is empty."""
        removes = self.browser.find_elements_by_class_name('js-remove')
        while removes:
            remove = removes[0]
            remove.click()
            self.wait.until(EC.staleness_of(remove))
            removes = self.browser.find_elements_by_class_name('js-remove')

        self.assertTrue(
            'Корзина пуста' in
            self.browser.find_element_by_class_name('js-order-contain').text
        )

    def test_table_and_dropdown_are_synchronized(self):
        def get_counts(browser=self.browser):
            table_count = (
                browser.find_element_by_id('cart-page-prods-count').text
            )
            header_count = (
                browser.find_element_by_class_name('js-cart-size').text
            )
            return table_count, header_count

        def update_count(update_xpath: str):
            table_count, header_count = get_counts()
            spin = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, update_xpath)
            ))
            spin.click()
            self.wait.until_not(EC.text_to_be_present_in_element(
                (By.ID, 'cart-page-prods-count'), table_count
            ))
            self.wait.until_not(EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'js-cart-size'), header_count
            ))

        def assert_count(count):
            table_count, dropdown_count = get_counts()
            self.assertIn(str(count), dropdown_count)
            self.assertIn(str(count), table_count)

        self.browser.refresh()
        assert_count(5)

        update_count(self.add_product)
        assert_count(6)

        update_count(self.remove_product)
        assert_count(4)

    # @todo #360:30m Resurrect test `test_confirm_order`
    @unittest.expectedFailure
    def test_confirm_order(self):
        """After filling the form we should be able to confirm an Order."""
        self.perform_operations_on_cart()
        self.fill_and_submit_form()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order-success', ))
        )

    @helpers.disable_celery
    def test_order_email(self):
        codes = self.browser.find_elements_by_class_name(
            'order-table-product-id')
        clean_codes = [code.text for code in codes]

        self.perform_operations_on_cart()
        final_price = self.browser.find_element_by_id('cart-page-sum').text[:-5]

        self.fill_and_submit_form()
        self.assertEqual(len(mail.outbox), 1)
        sent_mail_body = mail.outbox[0].body

        self.assertIn('Наличные', sent_mail_body)
        self.assertIn('+7 (222) 222 22 22', sent_mail_body)
        self.assertIn('test@test.test', sent_mail_body)
        for code in clean_codes:
            self.assertInHTML(
                '<td align="left"'
                'style="border-bottom:1px solid #E4E4E4;padding:10px">{0}</td>'
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


class SitePage(helpers.SeleniumTestCase):

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
        self.browser.delete_all_cookies()
        self.browser.get(self.live_server_url + self.page_last.url)
        wait_page_loading(self.browser)

    def tearDown(self):
        self.browser.execute_script('localStorage.clear();')

    @property
    def accordion_title(self):
        return self.browser.find_element_by_id(
            'js-accordion-title-{}'.format(self.page_top.id)
        )

    @property
    def accordion_content(self):
        return self.browser.find_element_by_id(
            'js-accordion-content-{}'.format(self.page_top.id)
        )

    def test_accordion_minimized(self):
        """Accordion item should be minimized by default."""
        self.assertFalse(self.accordion_content.is_displayed())

    def test_accordion_expand(self):
        """Accordion item should expand by click on title."""
        accordion_title = self.accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        self.wait.until(EC.visibility_of(accordion_content))

        self.assertTrue(accordion_content.is_displayed())

    def test_accordion_minimize_by_double_click(self):
        """Accordion item should be minimized by two clicks on title."""
        accordion_title = self.accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        self.wait.until(EC.visibility_of(accordion_content))
        accordion_title.click()
        self.wait.until_not(EC.visibility_of(accordion_content))

        self.assertFalse(accordion_content.is_displayed())


@helpers.disable_celery
@override_settings(DEBUG=True, INTERNAL_IPS=tuple())
class YandexMetrika(helpers.SeleniumTestCase):

    CART_LOCATOR = (By.CLASS_NAME, 'js-go-to-cart')

    def setUp(self):
        server = self.live_server_url
        product_vendor_code = Product.objects.first().vendor_code
        self.product_page = server + reverse('product', args=(product_vendor_code,))
        self.category_page = server + reverse(
            'category', args=(Category.objects.first().page.slug,))
        self.order_page_url = '{}{}'.format(
            self.live_server_url,
            reverse(Page.CUSTOM_PAGES_URL_NAME, args=('order',))
        )
        self.browser.get(self.live_server_url)
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
        self.wait.until(EC.url_to_be(self.order_page_url))

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
        self.buy_product()
        self.go_to_cart()
        self.prevent_default('submit', '#order-form-full')
        self.browser.find_element_by_id('id_phone').send_keys('22222222222')
        self.browser.find_element_by_id('id_email').send_keys('test@test.ru')
        self.browser.find_element_by_id('order-form-full').submit()

        self.assertTrue('FULL_BUY_SEND' in self.reached_goals)
        self.assertTrue('CMN_BUY_SEND' in self.reached_goals)

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


class Search(helpers.SeleniumTestCase):

    QUERY = 'Cate'
    INPUT_LOCATOR = (By.CLASS_NAME, 'js-search-input')

    def setUp(self):
        self.browser.get(self.live_server_url)
        wait_page_loading(self.browser)

    def tearDown(self):
        self.clear_input()

    @property
    def autocomplete(self):
        return self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'autocomplete-suggestions')
        ))

    @property
    def input(self):
        return self.wait.until(EC.visibility_of_element_located(
            self.INPUT_LOCATOR
        ))

    def fill_input(self, query=''):
        """Enter correct search term."""
        self.input.send_keys(query or self.QUERY)
        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'autocomplete-suggestions')
        ))

    def clear_input(self):
        """Enter correct search term."""
        self.input.send_keys(
            Keys.BACKSPACE * len(self.input.get_attribute('value'))
        )
        self.wait.until_not(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'autocomplete-suggestions')
        ))

    def search(self):
        self.browser.find_element_by_class_name('search-form').submit()
        self.wait.until(EC.url_contains('/search/'))
        self.wait.until(EC.visibility_of_element_located(
            (By.TAG_NAME, 'h1')
        ))

    def test_autocomplete_can_expand_and_collapse(self):
        self.fill_input()
        # fill input and autocomplete expands
        self.assertTrue(self.autocomplete.is_displayed())

        # remove search term ...
        self.clear_input()
        # ... and autocomplete collapse
        self.assertFalse(self.autocomplete.is_displayed())

    def test_autocomplete_item_link(self):
        """First autocomplete item should link on category page by click."""
        self.fill_input()
        self.click((By.CSS_SELECTOR, '.autocomplete-suggestions :first-child'))
        with self.screen_fail('test_autocomplete_item_link'):
            self.wait.until(EC.url_contains('/catalog/categories/'))

        self.assertTrue('/catalog/categories/' in self.browser.current_url)

    def test_autocomplete_see_all_item(self):
        """
        Autocomplete should contain "see all" item.

        `See all` item links on search results page.
        """
        self.fill_input()
        self.click((By.CLASS_NAME, 'autocomplete-last-item'))
        self.wait_page_loaded()

        self.assertTrue('/search/' in self.browser.current_url)

    def test_autocomplete_by_vendor_code(self):
        """Autocomplete should work by product's vendor code."""
        product_vendor_code = Product.objects.first().vendor_code

        self.fill_input(product_vendor_code)
        first_item = self.autocomplete.find_element_by_css_selector(':first-child')
        first_item.click()
        self.wait.until(EC.url_contains('/catalog/products/'))

        test_vendor_code = self.browser.find_element_by_class_name('product-article').text

        self.assertIn(str(product_vendor_code), test_vendor_code)

    # @todo #360:15m Resurrect test `test_search_have_results`
    @unittest.expectedFailure
    def test_search_have_results(self):
        """Search results page should contain links on relevant pages."""
        self.fill_input()
        self.search()

        self.assertTrue(self.browser.find_element_by_link_text(
            'Category #0 of #Category #0 of #Category #0'
        ))
        self.assertTrue(self.browser.find_element_by_link_text('Category #0'))

    def test_search_results_empty(self):
        """Search results for wrong term should contain empty result set."""
        self.input.send_keys('Not existing search query')
        self.search()

        h1 = self.browser.find_element_by_tag_name('h1')

        self.assertTrue(h1.text == 'По вашему запросу ничего не найдено')
