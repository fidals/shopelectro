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
from django.test import LiveServerTestCase

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


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json', 'admin.json']

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


class AdminPage(SeleniumTestCase):
    """Selenium-based tests for Admin page UI."""

    @classmethod
    def setUpClass(cls):
        super(AdminPage, cls).setUpClass()
        cls.admin_page = cls.live_server_url + reverse('admin:index')
        cls.change_products_url = cls.live_server_url + reverse(
            'admin:shopelectro_productpage_changelist')
        cls.login = 'admin'
        cls.password = 'asdfjkl;'
        cls.title_text = 'Shopelectro administration'
        cls.product_table = 'paginator'
        cls.active_products = '//*[@id="changelist-filter"]/ul[1]/li[2]/a'
        cls.inactive_products = '//*[@id="changelist-filter"]/ul[1]/li[3]/a'
        cls.price_filter = '//*[@id="changelist-filter"]/ul[2]/li[3]/a'
        cls.filter_by_has_content = '//*[@id="changelist-filter"]/ul[3]/li[2]/a'
        cls.filter_by_has_not_content = '//*[@id="changelist-filter"]/ul[3]/li[3]/a'
        cls.filter_by_has_image = '//*[@id="changelist-filter"]/ul[4]/li[2]/a'
        cls.filter_by_has_not_image = '//*[@id="changelist-filter"]/ul[4]/li[3]/a'
        cls.is_active_img = 'field-is_active'
        cls.autocomplete_text = 'Prod'

    def setUp(self):
        """Set up testing url and dispatch selenium webdriver."""
        self.root_category_id = str(Category.objects.filter(parent=None).first().id)
        self.children_category_id = str(Category.objects.filter(
            parent_id=self.root_category_id).first().id)
        self.deep_children_category_id = str(Category.objects.filter(
            parent_id=self.children_category_id).first().id)
        self.tree_product_id = str(Product.objects.filter(
            category_id=self.deep_children_category_id).first().id)

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

    def get_table_with_products(self):
        return self.browser.find_element_by_class_name(self.product_table)

    def open_js_tree_nodes(self):
        def get_change_state_button(id):
            return self.browser.find_element_by_id(id).find_element_by_tag_name('i')

        def change_state(id=None, class_name=None):
            if id:
                get_change_state_button(id).click()
                wait()
            else:
                self.browser.find_element_by_class_name(class_name).click()
                wait()

        def is_node_open(id):
            return self.browser.find_element_by_id(
                id).find_elements_by_class_name('jstree-children')

        def open_node(*args):
            for id in args:
                if not is_node_open(id):
                    # open node
                    change_state(id=id)

        if self.browser.find_elements_by_class_name('collapsed'):
            # Need to close sidebar
            change_state(class_name='js-toggle-sidebar')

        open_node(
            self.root_category_id, self.children_category_id, self.deep_children_category_id)

    def test_login(self):
        """We are able to login to Admin page."""

        admin_title = self.browser.find_element_by_id('site-name')
        self.assertIn(self.title_text, admin_title.text)

    def test_product_price_filter(self):
        """
        Price filter is able to filter products by set range.
        In this case we filter products with 1000 - 2000 price range.
        """
        # separated var for debugging
        self.browser.get(self.change_products_url)
        self.browser.find_element_by_xpath(self.price_filter).click()
        wait()
        product = self.browser.find_element_by_xpath('//*[@id="result_list"]/tbody/tr[1]/td[4]')
        product_price = int(float(product.text))

        self.assertTrue(product_price >= 1000)

    def test_image_filter(self):
        """
        Image filter is able to filter pages by the presence of the image.
        """
        self.browser.get(self.change_products_url)
        self.browser.find_element_by_xpath(self.filter_by_has_image).click()
        wait()

        table = self.get_table_with_products().text

        self.assertTrue('1' in table)

        self.browser.find_element_by_xpath(self.filter_by_has_not_image).click()
        wait()

        table = self.get_table_with_products().text

        self.assertTrue('299' in table)

    def test_content_filter(self):
        """
        Content filter is able to filter pages by the presence of the content.
        """
        self.browser.get(self.change_products_url)
        self.browser.find_element_by_xpath(self.filter_by_has_content).click()
        wait()

        table = self.browser.find_element_by_class_name(self.product_table).text

        self.assertTrue('0' in table)

        self.browser.find_element_by_xpath(self.filter_by_has_not_content).click()
        wait()

        table = self.get_table_with_products().text

        self.assertTrue('300' in table)

    def test_is_active_filter(self):
        """Activity filter returns only active or non active items."""

        self.browser.get(self.change_products_url)
        wait()
        self.browser.find_element_by_xpath(self.active_products).click()
        wait()

        first_product = self.browser.find_element_by_class_name(
            self.is_active_img).find_element_by_tag_name('img')
        first_product_state = first_product.get_attribute('alt')

        self.assertTrue(first_product_state == 'true')

        self.browser.find_element_by_xpath(self.inactive_products).click()
        wait()
        results = self.browser.find_element_by_class_name('paginator')

        self.assertTrue('0' in results.text)

    def test_search_autocomplete(self):
        """Search field should autocomplete."""

        self.browser.get(self.change_products_url)
        self.browser.find_element_by_id('searchbar').send_keys(self.autocomplete_text)
        wait()

        first_suggested_item = self.browser.find_element_by_class_name(
            'autocomplete-suggestion')
        first_suggested_item_text = first_suggested_item.get_attribute(
            'data-val')

        self.assertTrue(self.autocomplete_text in first_suggested_item_text)

    def test_sidebar_not_on_dashboard(self):
        """Sidebar should be not only on dashboard page."""

        self.browser.get(self.change_products_url)
        sidebar = self.browser.find_element_by_class_name('sidebar')

        self.assertTrue(sidebar.is_displayed())

    def test_tree_fetch_data(self):
        """Lazy load logic for jstree."""
        self.open_js_tree_nodes()
        node_children = (self.browser.find_element_by_id(self.deep_children_category_id)
                         .find_elements_by_class_name('jstree-leaf'))
        self.assertGreater(len(node_children), 10)

    def test_tree_redirect_to_entity_edit_page(self):
        """Test redirect to edit entity page by click on jstree's item."""
        self.open_js_tree_nodes()
        expected_h1 = ['Change category page', 'Изменить category page']

        # click at tree's item, redirect to entity edit page
        root_node = self.browser.find_element_by_id(self.root_category_id)
        root_node.find_element_by_tag_name('a').click()
        wait()
        test_h1 = self.browser.find_elements_by_tag_name('h1')[1].text

        self.assertIn(test_h1, expected_h1)

    def test_tree_redirect_to_table_editor_page(self):
        """Test redirect to table editor page by context click at tree's item"""
        self.open_js_tree_nodes()
        tree_item = self.browser.find_element_by_id(
            self.tree_product_id).find_element_by_tag_name('a')
        context_click(self.browser, tree_item)
        self.browser.find_elements_by_class_name('vakata-contextmenu-sep')[0].click()
        wait()

        test_h1 = self.browser.find_elements_by_tag_name('h1')[1].text
        self.assertEqual(test_h1, 'Table editor')

        test_search_value = self.browser.find_element_by_id('search-field').get_attribute('value')
        self.assertTrue(len(test_search_value) > 0)

    def test_tree_redirect_to_entity_site_page(self):
        """Test redirect to entity's site page by right bottom click at tree's item"""
        self.open_js_tree_nodes()
        tree_item = (self.browser.find_element_by_id(self.root_category_id)
                     .find_element_by_tag_name('a'))
        category_h1 = Category.objects.get(id=self.root_category_id).page.h1

        # open context menu and click at redirect to site's page
        context_click(self.browser, tree_item)
        self.browser.find_elements_by_class_name('vakata-contextmenu-sep')[1].click()
        wait()
        test_h1 = self.browser.find_element_by_tag_name('h1').text

        self.assertEqual(test_h1, category_h1)

    def test_sidebar_toggle(self):
        """Sidebar toggle button storage collapsed state."""

        self.browser.find_element_by_class_name('js-toggle-sidebar').click()
        wait()
        body_classes = self.browser.find_element_by_tag_name('body').get_attribute('class')

        self.assertTrue('collapsed' in body_classes)

        self.browser.refresh()
        wait()
        body_classes = self.browser.find_element_by_tag_name('body').get_attribute('class')

        self.assertTrue('collapsed' in body_classes)

    def test_yandex_feedback_request(self):
        """Send mail with request for leaving feedback on Ya.Market."""
        self.browser.find_element_by_class_name('js-toggle-sidebar').click()
        email_field = self.browser.find_element_by_id('user-email')
        email_field.send_keys(settings.EMAIL_HOST_USER + Keys.RETURN)
        wait()

        self.assertTrue('Письмо с отзывом успешно отправлено' in self.browser.page_source)


class TableEditor(SeleniumTestCase):
    """Selenium-based tests for Table Editor [TE]."""

    new_product_name = 'Product'

    @classmethod
    def setUpClass(cls):
        super(TableEditor, cls).setUpClass()
        cls.admin_page = cls.live_server_url + reverse('admin:index')
        cls.login = 'admin'
        cls.password = 'asdfjkl;'
        cls.autocomplete_text = 'Prod'

    def setUp(self):
        """Set up testing url and dispatch selenium webdriver."""
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
        self.browser.find_element_by_id('admin-editor-link').click()
        wait()

    def refresh_table_editor_page(self):
        self.browser.find_element_by_id('admin-editor-link').click()
        wait()

    def trigger_autocomplete(self, selector):
        """Programmatically trigger jQ autocomplete widget."""
        self.browser.execute_script(
            '$("' + selector + '").autocomplete("search");'
        )

    def update_input_value(self, index, new_data):
        """Clear input, pass new data and emulate Return keypress."""
        editable_input = self.browser.find_elements_by_class_name('inline-edit-cell')[index]
        editable_input.clear()
        editable_input.send_keys(new_data)
        editable_input.send_keys(Keys.ENTER)
        wait()

    def get_cell(self, index=0):
        """Return WebElement for subsequent manipulations by index."""
        table = self.browser.find_element_by_class_name('jqgrow')
        return table.find_elements_by_tag_name('td')[index]

    def get_current_price(self, index):
        """Return sliced integer price of first product by cell index."""
        raw_string = self.get_cell(index).text

        return int(''.join(raw_string.split(' '))[1:-3])

    def perform_checkbox_toggle(self, checkbox_name):
        """Change checkbox state by checkbox_name."""
        self.get_cell().click()
        checkbox = self.browser.find_element_by_name(checkbox_name)
        old_active_state = checkbox.is_selected()
        checkbox.click()
        checkbox.send_keys(Keys.ENTER)
        self.refresh_table_editor_page()

        self.get_cell().click()
        new_active_state = self.browser.find_element_by_name(checkbox_name).is_selected()

        return old_active_state, new_active_state

    def open_filters(self):
        """Open TE filters cause they are collapsed by default."""
        filters_wrapper = self.browser.find_element_by_class_name('js-filter-wrapper')

        if not filters_wrapper.is_displayed():
            self.browser.find_element_by_class_name('js-hide-filter').click()
            wait()

    def check_filters_and_table_headers_equality(self):
        """TE filters and table headers text should be equal."""
        filters = self.browser.find_elements_by_class_name('js-sortable-item')

        for index, item in enumerate(filters):
            filter_text = item.text.lower()
            table_header_text = self.browser.find_elements_by_class_name('ui-th-div')[index + 1].text.lower()

            self.assertIn(table_header_text, filter_text)

    def add_col_to_grid(self, col_name):
        filter_fields = self.browser.find_elements_by_class_name('filter-fields-label')

        def is_correct_col(col):
            return col_name in col.get_attribute('for')

        next(filter(is_correct_col, filter_fields)).click()
        self.save_filters()

    def save_filters(self):
        self.browser.find_element_by_class_name('js-save-filters').click()
        wait(2)

    def test_products_loaded(self):
        """TE should have all products."""
        rows = self.browser.find_elements_by_class_name('jqgrow')

        self.assertTrue(len(rows) > 0)

    def test_edit_product_name(self):
        """We could change Product name from TE."""
        self.get_cell(1).click()
        self.update_input_value(0, self.new_product_name)
        self.refresh_table_editor_page()
        updated_name = self.get_cell(1).text

        self.assertEqual(updated_name, self.new_product_name)

    def test_edit_product_price(self):
        """We could change Product price from TE."""
        price_cell_index = 3
        price_cell_input = 2
        new_price = self.get_current_price(price_cell_index) + 100
        self.get_cell(price_cell_index).click()
        wait()
        self.update_input_value(price_cell_input, new_price)
        self.refresh_table_editor_page()
        updated_price = self.get_current_price(price_cell_index)

        self.assertEqual(updated_price, new_price)

    def test_edit_product_activity(self):
        """We could change Product is_active state from TE."""
        self.open_filters()
        self.add_col_to_grid('is_active')
        old_active_state, new_active_state = self.perform_checkbox_toggle('page_is_active')

        self.assertNotEqual(new_active_state, old_active_state)

    def test_edit_product_popularity(self):
        """We could change Product price is_popular state from TE."""
        self.open_filters()
        self.add_col_to_grid('is_popular')
        old_popular_state, new_popular_state = self.perform_checkbox_toggle('is_popular')

        self.assertNotEqual(new_popular_state, old_popular_state)

    def test_remove_product(self):
        """We could remove Product from TE."""
        old_first_row_id = self.get_cell().text
        self.browser.find_element_by_class_name('js-confirm-delete-modal').click()
        wait()
        self.browser.find_element_by_class_name('js-modal-delete').click()
        wait()
        new_first_row_id = self.get_cell().text

        self.assertNotEqual(old_first_row_id, new_first_row_id)

    def test_sort_table_by_id(self):
        """We could sort products in TE by id."""
        first_product_id_before = self.get_cell().text
        self.browser.find_element_by_class_name('ui-jqgrid-sortable').click()
        self.browser.find_element_by_class_name('ui-jqgrid-sortable').click()
        first_product_id_after = self.get_cell().text

        self.assertNotEqual(first_product_id_before, first_product_id_after)

    def test_sort_table_by_price(self):
        """We could sort products in TE by price."""
        first_product_price_before = self.get_cell(1).text
        name_header = self.browser.find_elements_by_class_name('ui-jqgrid-sortable')[1]
        name_header.click()
        name_header.click()
        first_product_price_after = self.get_cell(1).text

        self.assertNotEqual(first_product_price_before, first_product_price_after)

    def test_filter_table(self):
        """We could make live search in TE."""
        rows_before = len(self.browser.find_elements_by_class_name('jqgrow'))
        search_field = self.browser.find_element_by_id('search-field')
        search_field.send_keys('384')
        wait(2)
        rows_after = len(self.browser.find_elements_by_class_name('jqgrow'))

        self.assertNotEqual(rows_before, rows_after)

    def test_filters_equals_table_headers(self):
        """Headers in TE should be equal to chosen filters respectively."""
        self.open_filters()
        self.check_filters_and_table_headers_equality()

    def test_save_and_drop_custom_filters(self):
        """
        Headers in TE should be generated based on user settings in localStorage.

        This test case is contains save & drop cases cause they are depends on each other.
        """
        self.browser.refresh()
        self.open_filters()

        checkboxes = self.browser.find_elements_by_class_name('filter-fields-item')

        for index, item in enumerate(checkboxes):
            self.browser.find_elements_by_class_name('filter-fields-item')[index].click()

        self.save_filters()
        self.check_filters_and_table_headers_equality()

        self.browser.refresh()
        self.open_filters()
        wait(2)

        self.browser.find_element_by_class_name('js-drop-filters').click()
        wait(2)
        self.check_filters_and_table_headers_equality()

    def test_non_existing_category_change(self):
        """We should see popover after trying to change Product's category to non existing one."""
        self.get_cell().click()
        self.update_input_value(3, 'yo')

        popover = self.browser.find_element_by_class_name('webui-popover')

        self.assertTrue(popover.is_displayed())

    def test_new_entity_creation(self):
        new_entity_text = 'A New stuff'
        prices = [
            'entity-price', 'entity-wholesale-small',
            'entity-wholesale-medium', 'entity-wholesale-large'
        ]

        # Trigger entity creation modal & input data:
        self.browser.find_element_by_css_selector('button[data-target="#add-entity"]').click()
        self.browser.find_element_by_id('entity-name').send_keys(new_entity_text)
        for price in prices:
            self.browser.find_element_by_id(price).send_keys(123)

        # Check is autocomplete works for category search by manual triggering it:
        self.browser.find_element_by_id('entity-category').send_keys('Category #0')
        wait()
        self.trigger_autocomplete('#entity-category')
        wait()
        autocomplete = self.browser.find_element_by_class_name('ui-autocomplete')

        # Choose category from autocomplete dropdown & save new entity:
        autocomplete.find_element_by_class_name('ui-menu-item-wrapper').click()
        self.browser.find_element_by_id('entity-save').click()
        wait()

        # If entity was successfully changed `refresh_btn` should become active:
        refresh_btn = self.browser.find_element_by_id('refresh-table')
        self.assertFalse(refresh_btn.get_attribute('disabled'))

        # After click on `refresh_btn` TE should be updated:
        refresh_btn.click()
        self.browser.find_element_by_class_name('js-modal-close').click()
        wait()
        first_row = self.browser.find_element_by_id('jqGrid').find_element_by_class_name('jqgrow')
        name_cell = first_row.find_elements_by_tag_name('td')[1]
        self.assertEqual(name_cell.get_attribute('title'), new_entity_text)

        # We are able to change newly created entity:
        self.test_edit_product_name()
