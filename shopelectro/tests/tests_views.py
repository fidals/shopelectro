"""
Views tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.

All Selenium-tests should live in tests_selenium.
"""
from xml.etree import ElementTree as ET
from functools import partial

from django.contrib.redirects.models import Redirect
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from pages.models import FlatPage
from shopelectro.models import CategoryPage, ProductPage
from shopelectro.views.service import generate_md5_for_ya_kassa, YANDEX_REQUEST_PARAM


class SitemapPage(TestCase):
    """
    Tests for Sitemap.
    Getting sitemap.xml and parsing it as string.
    """

    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        """Import testing data into DB and create site domain name."""
        call_command('redirects')

        # Namespace for using ET.find()
        cls.NAMESPACE = '{http://www.sitemaps.org/schemas/sitemap/0.9}'

    @classmethod
    def tearDownClass(cls):
        Redirect.objects.all().delete()

    def setUp(self):
        """Sets up testing url."""

        content = self.client.get('/sitemap.xml').content.decode('utf-8')
        self.root = ET.fromstring(content)

    def test_url_tags(self):
        """We should see <url> tags on Sitemap page."""
        url_tags = self.root.findall('{}url'.format(self.NAMESPACE))
        self.assertGreater(len(url_tags), 0)

    def test_models_urls(self):
        """Sitemap page should to print correct urls for models."""
        slice_start_index = len('https://' + settings.SITE_DOMAIN_NAME)

        path = '{0}url[2]/{0}loc'.format(self.NAMESPACE)
        model_url_text = self.root.find(path).text[slice_start_index:]
        response = self.client.get(model_url_text)

        self.assertEqual(response.status_code, 200)

class AdminPage(TestCase):
    """Tests for Admin page UI."""

    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        super(AdminPage, cls).setUpClass()
        cls.username = 'admin'
        cls.email = 'admin@admin.com'
        cls.password = 'asdfjkl'

        cls.list_display = {
            'page': ['Id', 'H1', 'Parent', 'Is active', ],
            'product': ['Id', 'H1', 'Category', 'Price', 'Link', 'Is active', ],
            'category': ['Id', 'H1', 'Parent', 'Is active', ],
        }

        cls.fieldsets = {
            'page': ['Position', 'Content', 'title', 'Keywords', 'Description', 'Is active',
                     'Seo text', 'h1'],
            'product': ['Name', 'Category', 'Price', 'ID', 'Purchase price', 'Wholesale large',
                        'Wholesale medium', 'Wholesale small', 'In stock', 'Is popular', ],
            'category': ['Name', 'Parent', 'Position', 'ID', ],
        }

    def setUp(self):
        self.user = User.objects.create_superuser(self.username, self.email, self.password)
        self.client.login(username=self.username, password=self.password)

    def tearDown(self):
        self.user.delete()

    def test_flat_page_changelist_display_list(self):
        """
        Pages model's changelist-page must have all needed columns, which was define
        in Admin.py
        """
        response = self.client.get(
            reverse('custom_admin:pages_flatpage_changelist'))

        for field in self.list_display['page']:
            self.assertContains(response, field)

    def test_flat_page_change_fieldset(self):
        """Pages model's change-page must have all needed fields, which was define in Admin.py"""
        response = self.client.get(
            reverse(
                'custom_admin:pages_flatpage_change', args=(FlatPage.objects.filter().first().id, )
            )
        )

        self.assertNotContains(response, 'Products')
        self.assertNotContains(response, 'Categories')

        for field in self.fieldsets['page']:
            self.assertContains(response, field)

    def test_category_page_changelist_display_list(self):
        """
        Categories model's changelist-page must have all needed columns, which was define
        in Admin.py
        """
        response = self.client.get(
            reverse('custom_admin:shopelectro_categorypage_changelist'))

        for field in self.list_display['category']:
            self.assertContains(response, field)

    def test_category_page_change_fieldset(self):
        """
        Categories model's change-page must have all needed fields, which was define in Admin.py
        """
        response = self.client.get(
            reverse(
                'custom_admin:shopelectro_categorypage_change', args=(
                    CategoryPage.objects.filter().first().id,
                )
            )
        )

        self.assertNotContains(response, 'Products')

        for field in self.fieldsets['category']:
            self.assertContains(response, field)

        for field in self.fieldsets['page']:
            self.assertContains(response, field)

    def test_products_changelist_display_list(self):
        """
        Products model's changelist-page must have all needed columns, which was define
        in Admin.py
        """
        response = self.client.get(
            reverse('custom_admin:shopelectro_productpage_changelist'))

        for field in self.list_display['product']:
            self.assertContains(response, field)

    def test_products_change_fieldset(self):
        """Products model's change-page must have all needed fields, which was define in Admin.py"""
        response = self.client.get(
            reverse(
                'custom_admin:shopelectro_productpage_change', args=(
                    ProductPage.objects.filter().first().id,
                )
            )
        )

        self.assertNotContains(response, 'Categories')

        for field in self.fieldsets['product']:
            self.assertContains(response, field)

        for field in self.fieldsets['page']:
            self.assertContains(response, field)


class YandexKassa(TestCase):
    """
    Tests for yandex check order and yandex aviso
    Yandex docs https://goo.gl/bOf3kw
    """

    fixtures = ['dump.json']

    def create_aviso_request_data(self):
        data_for_md5 = {param: str(number) for number, param in enumerate(YANDEX_REQUEST_PARAM)}
        data_for_md5.update({'shopPassword': settings.YANDEX_SHOP_PASS})
        md5 = generate_md5_for_ya_kassa(data_for_md5)
        request_data = {
            'md5': md5,
            'orderSumAmount': '12312',
            'shopSumAmount': '123123',
            **data_for_md5,
        }
        return request_data

    def setUp(self):
        self.yandex_aviso_request_data = {
            'path': reverse('yandex_aviso'),
            'data': self.create_aviso_request_data()
        }
        self.yandex_check_request_data = {
            'path': reverse('yandex_check'),
            'data': {'invoiceId': 123}
        }

        self.yandex_aviso_request = partial(self.client.post, **self.yandex_aviso_request_data)
        self.yandex_check_request = partial(self.client.post, **self.yandex_check_request_data)


    def test_yandex_check_body(self):
        """Respose should contain attr code="0" - it's mean, that all right"""
        response = self.yandex_check_request()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'code="0"')
        self.assertContains(response, 'invoiceId="123"')

    def test_yandex_aviso_body(self):
        """
        Response should contain attr code="0" - it's mean, that all right, if code="1" - it's mean,
        yandex's request body contain incorrect data.
        """
        response = self.yandex_aviso_request()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'code="0"')

        self.yandex_aviso_request_data['data']['md5'] = 'incorrect data'
        response = self.yandex_aviso_request()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'code="1"')
