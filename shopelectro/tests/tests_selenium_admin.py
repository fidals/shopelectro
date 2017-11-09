"""
Selenium-based tests.

If you need to create new test-suite, subclass it from SeleniumTestCase class.
Every Selenium-based test suite uses fixture called dump.json.
"""

from django.conf import settings
from django.urls import reverse
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from shopelectro.models import Category, Product
from shopelectro.tests import helpers


class AdminSeleniumTestCase(helpers.SeleniumTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json', 'admin.json']

    login = 'admin'
    password = 'asdfjkl;'

    def wait_page_loading(self):
        self.wait.until(EC.presence_of_element_located(
            (By.TAG_NAME, 'body')
        ))

    def signin(self):
        self.browser.delete_all_cookies()
        with self.screen_fail('sign_in_admin'):
            self.browser.get(self.admin_page)
        self.wait_page_loading()
        login_field = self.browser.find_element_by_id('id_username')
        login_field.clear()
        login_field.send_keys(self.login)
        password_field = self.browser.find_element_by_id('id_password')
        password_field.clear()
        password_field.send_keys(self.password)
        login_form = self.browser.find_element_by_id('login-form')
        login_form.submit()
        self.wait_page_loading()

    @property
    def admin_page(self):
        raise NotImplemented()

    def setUp(self):
        self.signin()


@helpers.enable_russian_language
class AdminPage(AdminSeleniumTestCase):
    """Selenium-based tests for Admin page UI."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_page = cls.live_server_url + reverse('admin:index')
        cls.change_products_url = cls.live_server_url + reverse(
            'admin:shopelectro_productpage_changelist')
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
        cls.jstree_children = 'jstree-children'

    def setUp(self):
        super().setUp()
        self.root_category_id = str(Category.objects.filter(parent=None).first().id)
        self.children_category_id = str(Category.objects.filter(
            parent_id=self.root_category_id).first().id)
        self.deep_children_category_id = str(Category.objects.filter(
            parent_id=self.children_category_id).first().id)
        self.tree_product_id = str(Product.objects.filter(
            category_id=self.deep_children_category_id).first().id)

    def tearDown(self):
        self.browser.execute_script('localStorage.clear();')

    def open_side_bar(self):
        if self.browser.find_elements_by_class_name('collapsed'):
            self.browser.find_element_by_class_name('js-toggle-sidebar').click()

    def open_js_tree_nodes(self):

        def get_node(id):
            return self.wait.until(EC.visibility_of_element_located((By.ID, id)))

        def open_node(node):
            return node.find_element_by_tag_name('i').click()

        def open_nodes(*args):
            for id_ in args:
                open_node(get_node(id_))

        self.open_side_bar()
        open_nodes(
            self.root_category_id,
            self.children_category_id,
            self.deep_children_category_id
        )
        self.wait.until(EC.visibility_of_element_located(
            (By.ID, self.tree_product_id)
        ))

    def get_table_with_products(self):
        return self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, self.product_table)
        ))

    def click_jstree_context_menu_items(self, item_index):
        def get_tree_item():
            return (
                self.browser
                .find_element_by_id(self.children_category_id)
                .find_element_by_tag_name('ul')
                .find_element_by_tag_name('a')
            )
        helpers.context_click(self.browser, get_tree_item())
        self.wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'vakata-contextmenu-sep')
        ))[item_index].click()
        id_, _ = get_tree_item().get_attribute('id').split('_')
        return int(id_)

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
        self.wait_page_loading()

        self.browser.find_element_by_xpath(self.price_filter).click()
        product = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="result_list"]/tbody/tr[1]/td[4]')
        ))
        product_price = int(float(product.text.replace(',', '.')))

        self.assertTrue(product_price >= 1000)

    def test_image_filter(self):
        """Image filter is able to filter pages by the presence of the image."""
        self.browser.get(self.change_products_url)
        self.wait_page_loading()

        self.browser.find_element_by_xpath(self.filter_by_has_image).click()
        table = self.get_table_with_products().text

        self.assertTrue('1' in table)

        self.browser.find_element_by_xpath(self.filter_by_has_not_image).click()
        table = self.get_table_with_products().text

        self.assertTrue('299' in table)

    def test_content_filter(self):
        """Content filter is able to filter pages by the presence of the content."""
        self.browser.get(self.change_products_url)
        self.wait_page_loading()

        self.browser.find_element_by_xpath(self.filter_by_has_content).click()
        table = self.get_table_with_products().text

        self.assertTrue('0' in table)

        self.browser.find_element_by_xpath(self.filter_by_has_not_content).click()
        table = self.get_table_with_products().text

        self.assertTrue('300' in table)

    def test_is_active_filter(self):
        """Activity filter returns only active or non active items."""
        self.browser.get(self.change_products_url)
        self.wait_page_loading()

        self.browser.find_element_by_xpath(self.active_products).click()
        first_product_state = (
            self.wait
            .until(EC.presence_of_element_located((By.CLASS_NAME, self.is_active_img)))
            .find_element_by_tag_name('img')
            .get_attribute('alt')
        )

        self.assertTrue(first_product_state == 'true')

        self.browser.find_element_by_xpath(self.inactive_products).click()
        results = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'paginator'))
        )

        self.assertTrue('0' in results.text)

    def test_search_autocomplete(self):
        """Search field should autocomplete."""
        self.browser.get(self.change_products_url)
        self.wait_page_loading()

        self.browser.find_element_by_id('searchbar').send_keys(self.autocomplete_text)
        first_suggested_item_text = (
            self.wait
            .until(EC.presence_of_element_located((By.CLASS_NAME, 'autocomplete-suggestion')))
            .get_attribute('data-val')
        )

        self.assertTrue(self.autocomplete_text in first_suggested_item_text)

    def test_sidebar_not_on_dashboard(self):
        """Sidebar should be not only on dashboard page."""
        self.browser.get(self.change_products_url)
        self.wait_page_loading()

        sidebar = self.browser.find_element_by_class_name('sidebar')

        self.assertTrue(sidebar.is_displayed())

    def test_tree_fetch_data(self):
        """Lazy load logic for jstree."""
        self.wait_page_loading()

        self.open_js_tree_nodes()
        node_children = (
            self.browser
            .find_element_by_id(self.deep_children_category_id)
            .find_elements_by_class_name('jstree-leaf')
        )

        self.assertGreater(len(node_children), 10)

    def test_tree_redirect_to_entity_edit_page(self):
        """Test redirect to edit entity page by click on jstree's item."""
        self.wait_page_loading()
        self.open_js_tree_nodes()
        expected_h1 = ['Change category page', 'Изменить category page']

        # click at tree's item, redirect to entity edit page
        (
            self.browser
            .find_element_by_id(self.root_category_id)
            .find_element_by_tag_name('a')
            .click()
        )
        test_h1 = self.wait.until(EC.presence_of_all_elements_located(
            (By.TAG_NAME, 'h1')
        ))[1].text

        self.assertIn(test_h1, expected_h1)

    def test_tree_redirect_to_table_editor_page(self):
        """Test redirect to table editor page by context click at tree's item."""
        self.wait_page_loading()
        self.open_js_tree_nodes()
        self.click_jstree_context_menu_items(0)
        self.wait.until(EC.url_contains('/editor/'))
        test_h1 = self.wait.until(EC.presence_of_all_elements_located(
            (By.TAG_NAME, 'h1')
        ))[1].text

        self.assertEqual(test_h1, 'Табличный редактор')

        test_search_value = (
            self.browser
            .find_element_by_id('search-field')
            .get_attribute('value')
        )
        self.assertTrue(len(test_search_value) > 0)

    def test_tree_redirect_to_entity_site_page(self):
        """Test redirect to entity's site page from jsTree context menu."""
        self.wait_page_loading()
        self.open_js_tree_nodes()
        # open context menu and click at redirect to site's page
        item_id = self.click_jstree_context_menu_items(1)
        category_id = Category.objects.get(id=item_id).page.display_h1
        # wait new tab opening
        self.wait.until(EC.number_of_windows_to_be(2))
        self.browser.switch_to.window(window_name=self.browser.window_handles[1])
        test_h1 = self.wait.until(EC.presence_of_element_located(
            (By.TAG_NAME, 'h1')
        )).text

        self.assertEqual(test_h1, category_id)

    def test_sidebar_toggle(self):
        """Sidebar toggle button storage collapsed state."""
        self.wait_page_loading()

        self.browser.find_element_by_class_name('js-toggle-sidebar').click()
        body_classes = self.browser.find_element_by_tag_name('body').get_attribute('class')
        self.assertTrue('collapsed' in body_classes)

        self.browser.refresh()
        self.wait_page_loading()
        body_classes = self.browser.find_element_by_tag_name('body').get_attribute('class')
        self.assertTrue('collapsed' in body_classes)

    @helpers.disable_celery
    def test_yandex_feedback_request(self):
        """Send mail with request for leaving feedback on Ya.Market."""
        self.wait_page_loading()
        self.open_side_bar()
        email_field = self.browser.find_element_by_id('user-email')
        email_field.send_keys(settings.EMAIL_HOST_USER + Keys.RETURN)

        self.assertTrue('Письмо с отзывом успешно отправлено' in self.browser.page_source)


@helpers.enable_russian_language
class TableEditor(AdminSeleniumTestCase):
    """Selenium-based tests for Table Editor [TE]."""

    new_product_name = 'Product'

    @classmethod
    def setUpClass(cls):
        super(TableEditor, cls).setUpClass()
        cls.autocomplete_text = 'Prod'
        cls.filter_wrapper_class = 'js-filter-wrapper'

    def setUp(self):
        """Set up testing url and dispatch selenium webdriver."""
        super().setUp()
        self.wait.until(EC.presence_of_element_located(
            (By.ID, 'admin-editor-link')
        ))
        self.browser.find_element_by_id('admin-editor-link').click()
        self.wait_tableeditor_loading()

    @property
    def admin_page(self):
        return self.live_server_url + reverse('admin:index')

    def wait_tableeditor_loading(self):
        self.wait_page_loading()
        self.wait.until(EC.invisibility_of_element_located(
            (By.ID, 'load_jqGrid')
        ))

    def refresh_table_editor_page(self):
        self.browser.find_element_by_id('admin-editor-link').click()
        self.wait_tableeditor_loading()

    def trigger_autocomplete(self, selector):
        """Trigger jQ autocomplete widget."""
        self.browser.execute_script(
            '$("' + selector + '").autocomplete("search");'
        )

    def update_input_value(self, cell_index, new_data):
        """Clear input, pass new data and emulate Return keypress."""
        cell = self.get_cell(cell_index)
        cell.click()

        expect_editable_cells = EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'inline-edit-cell')
        )
        self.wait.until(expect_editable_cells)

        input_el = self.get_cell(cell_index).find_element_by_tag_name('input')
        input_el.clear()
        input_el.send_keys(new_data)
        input_el.send_keys(Keys.ENTER)

        self.wait.until_not(expect_editable_cells)

    def get_cell(self, index=0):
        """Return WebElement for subsequent manipulations by index."""
        table = self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'jqgrow')
        ))
        return table.find_elements_by_tag_name('td')[index]

    def get_current_price(self, cell):
        """Return sliced integer price of first product by cell index."""
        return int(''.join(cell.text.split(' '))[1:-3])

    def perform_checkbox_toggle(self, checkbox_name):
        """Change checkbox state by checkbox_name."""
        self.get_cell(2).click()
        find_checkbox = EC.presence_of_element_located((By.NAME, checkbox_name))
        checkbox = self.wait.until(find_checkbox)
        old_active_state = checkbox.is_selected()
        checkbox.click()
        checkbox.send_keys(Keys.ENTER)
        self.refresh_table_editor_page()

        self.get_cell(2).click()
        new_active_state = self.wait.until(find_checkbox).is_selected()

        return old_active_state, new_active_state

    def open_filters(self):
        """Open TE filters cause they are collapsed by default."""
        filters_wrapper = self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, self.filter_wrapper_class)
        ))

        if not filters_wrapper.is_displayed():
            self.browser.find_element_by_class_name('js-hide-filter').click()
            self.wait.until(EC.visibility_of_element_located(
                (By.CLASS_NAME, self.filter_wrapper_class)
            ))

    def check_filters_and_table_headers_equality(self):
        """TE filters and table headers text should be equal."""
        filters = self.browser.find_elements_by_class_name('js-sortable-item')

        for index, item in enumerate(filters):
            filter_text = item.text.lower()
            table_header_text = (
                self.browser.find_elements_by_class_name('ui-th-div')[index + 1].text.lower()
            )

            self.assertIn(table_header_text, filter_text)

    def add_col_to_grid(self, col_name):
        filter_fields = self.wait.until(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, 'filter-fields-label')
        ))

        def is_correct_col(col):
            return col_name in col.get_attribute('for')

        next(filter(is_correct_col, filter_fields)).click()
        self.save_filters()

    def save_filters(self):
        self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'js-save-filters')
        )).click()
        self.wait_tableeditor_loading()

    def test_products_loaded(self):
        """TE should have all products."""
        rows = self.browser.find_elements_by_class_name('jqgrow')

        self.assertTrue(len(rows) > 0)

    def test_edit_product_name(self):
        """We could change Product name from TE."""
        self.update_input_value(2, self.new_product_name)
        self.refresh_table_editor_page()
        updated_name = self.get_cell(2).text

        self.assertEqual(updated_name, self.new_product_name)

    def test_edit_product_price(self):
        """We could change Product price from TE."""
        price_cell_index = 3
        cell = self.get_cell(price_cell_index)
        new_price = self.get_current_price(self.get_cell(price_cell_index)) + 100
        self.update_input_value(price_cell_index, new_price)
        self.refresh_table_editor_page()
        cell = self.get_cell(price_cell_index)
        updated_price = self.get_current_price(cell)

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
        old_first_row = self.get_cell()
        old_first_row_id = old_first_row.text
        self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'js-confirm-delete-modal')
        )).click()
        self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'js-modal-delete')
        )).click()
        self.wait.until(EC.staleness_of(old_first_row))

        new_first_row_id = self.get_cell().text
        self.assertNotEqual(old_first_row_id, new_first_row_id)

    def test_sort_table_by_id(self):
        """We could sort products in TE by id."""
        first_product_id_before = self.get_cell().text
        id_header = self.wait.until(EC.element_to_be_clickable(
            (By.ID, 'jqgh_jqGrid_id')
        ))
        id_header.click()
        id_header.click()
        first_product_id_after = self.get_cell().text

        self.assertNotEqual(first_product_id_before, first_product_id_after)

    def test_sort_table_by_price(self):
        """We could sort products in TE by price."""
        first_product_price_before = self.get_cell(1).text
        name_header = self.wait.until(EC.element_to_be_clickable(
            (By.ID, 'jqgh_jqGrid_price')
        ))
        name_header.click()
        name_header.click()
        first_product_price_after = self.get_cell(3).text

        self.assertNotEqual(first_product_price_before, first_product_price_after)

    def test_filter_table(self):
        """We could make live search in TE."""
        rows_before = len(self.browser.find_elements_by_class_name('jqgrow'))
        id_ = '138'
        search_field = self.browser.find_element_by_id('search-field')
        search_field.send_keys(id_)
        self.wait.until(EC.text_to_be_present_in_element(
            (By.ID, id_), id_
        ))
        rows_after = len(self.browser.find_elements_by_class_name('jqgrow'))

        self.assertNotEqual(rows_before, rows_after)

    def test_filters_equals_table_headers(self):  # Ignore PyDocStyleBear
        """Headers in TE should be equal to chosen filters respectively."""
        self.open_filters()
        self.check_filters_and_table_headers_equality()

    def test_save_and_drop_custom_filters(self):  # Ignore PyDocStyleBear
        """
        Headers in TE should be generated based on user settings in localStorage.

        This test case is contains save & drop cases cause they are depends on each other.
        """
        self.browser.refresh()
        self.open_filters()

        checkboxes = self.browser.find_elements_by_class_name('filter-fields-item')

        for index in range(len(checkboxes)):
            self.browser.find_elements_by_class_name('filter-fields-item')[index].click()

        self.save_filters()
        self.check_filters_and_table_headers_equality()

        self.browser.refresh()
        self.open_filters()
        self.browser.find_element_by_class_name('js-drop-filters').click()
        self.wait_tableeditor_loading()
        self.check_filters_and_table_headers_equality()

    def test_non_existing_category_change(self):
        """We should see popover after trying to change Product's category to non existing one."""
        self.update_input_value(4, 'yo')

        popover = self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'webui-popover')
        ))

        self.assertTrue(popover.is_displayed())

    def test_new_entity_creation(self):
        new_entity_text = 'A New stuff'
        numeric_fields = [
            'entity-price', 'entity-wholesale-small',
            'entity-wholesale-medium', 'entity-wholesale-large',
            'entity-vendor-code'
        ]

        # Trigger entity creation modal & input data:
        ActionChains(self.browser).move_to_element(
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[data-target="#add-entity"]')
            ))
        ).click().perform()
        with self.screen_fail('test_new_entity_creation'):
            self.wait.until(EC.visibility_of_element_located(
                (By.ID, 'add-entity-form')
            ))

        self.browser.find_element_by_id('entity-name').send_keys(new_entity_text)
        for field in numeric_fields:
            self.browser.find_element_by_id(field).send_keys(123)

        # Check is autocomplete works for category search by manual triggering it:
        self.browser.find_element_by_id('entity-category').send_keys('Category #0')
        self.trigger_autocomplete('#entity-category')
        autocomplete = self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'ui-autocomplete')
        ))

        # Choose category from autocomplete dropdown & save new entity:
        autocomplete.find_element_by_class_name('ui-menu-item-wrapper').click()
        self.wait.until(EC.element_to_be_clickable(
            (By.ID, 'entity-save')
        ))
        self.browser.find_element_by_id('entity-save').click()

        self.wait.until_not(EC.element_to_be_clickable((By.ID, 'entity-save')))

        # If entity was successfully changed `refresh_btn` should become active:
        refresh_btn = self.browser.find_element_by_id('refresh-table')
        self.assertFalse(refresh_btn.get_attribute('disabled'))

        # After click on `refresh_btn` TE should be updated:
        refresh_btn.click()
        fade_in = self.browser.find_element_by_class_name('modal-backdrop')
        self.browser.find_element_by_class_name('js-modal-close').click()
        self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'modal-box')))
        self.wait.until(EC.staleness_of(fade_in))
        name_cell = self.get_cell(2)
        self.assertEqual(name_cell.get_attribute('title'), new_entity_text)

        # We are able to change newly created entity:
        self.test_edit_product_name()
