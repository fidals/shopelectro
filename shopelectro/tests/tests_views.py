"""
Views tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.

All Selenium-tests should live in tests_selenium.
"""
from functools import partial
from itertools import chain
from operator import attrgetter
from xml.etree import ElementTree as ET

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.test import TestCase
from django.test.utils import override_settings

from pages.models import FlatPage

from shopelectro.models import CategoryPage, ProductPage, Category, Product, Tag
from shopelectro.views.service import generate_md5_for_ya_kassa, YANDEX_REQUEST_PARAM


# TODO: remove override_settings after dev-828.
@override_settings(DEBUG=True)
class CatalogPage(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.category = Category.objects.root_nodes().first()

    def test_category_page_contains_all_tags(self):
        """Category contains all Product's tags."""
        response = self.client.get(reverse('category', args=(self.category.page.slug, )))

        tags = set(chain.from_iterable(map(
            lambda x: x.tags.all(), Product.objects.get_by_category(self.category)
        )))

        tag_names = list(map(attrgetter('name'), tags))

        for tag_name in tag_names:
            self.assertContains(response, tag_name)

    def test_product_by_certain_tags(self):
        """Category page contains Product's related by certain tags."""
        first_tag, last_tag = Tag.objects.all().first(), Tag.objects.last()
        response = self.client.get(
            reverse('category', args=(self.category.page.slug, )),
            {'tags': [first_tag.id, last_tag.id]}
        )

        products_count = len(list(filter(
            lambda x: x.category.is_descendant_of(self.category),
            Product.objects.filter(Q(tags=first_tag) & Q(tags=last_tag))
        )))

        self.assertContains(response, products_count)


class SitemapXML(TestCase):
    """
    Tests for Sitemap XML.
    Getting sitemap.xml and parsing it as string.
    """

    fixtures = ['dump.json']

    def setUp(self):
        """Set up testing url."""
        # Namespace for using ET.find()
        self.NAMESPACE = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
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


class SitemapPage(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.response = self.client.get('/sitemap/')

    def test_pagination_on_page(self):
        paginator_pages = self.response.context['paginator_pages']
        paginator_links = self.response.context['paginator_links']

        self.assertTrue(len(paginator_pages) == 50)
        self.assertFalse(len(paginator_links) == 0)

    def test_sitemap_self_link_on_page(self):
        sitemap_url_slug = reverse('custom_page', args=('sitemap', ))
        self.assertIn(sitemap_url_slug, self.response.content.decode('utf-8'))


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
            'page': ['ID', 'Name', 'Parent', 'Is active', ],
            'product': ['Id', 'Name', 'Category', 'Price', 'Link', 'Is active', ],
            'category': ['Id', 'Name', 'Parent', 'Is active', ],
        }

        cls.fieldsets = {
            'page': ['Position', 'Content', 'title', 'Keywords', 'Description', 'Is active',
                     'Seo text', 'h1', 'Name'],
            'product': ['Name', 'Category', 'Price', 'ID', 'Purchase price', 'Wholesale large',
                        'Wholesale medium', 'Wholesale small', 'In stock', 'Is popular', 'Tags'],
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
            reverse('se_admin:pages_flatpage_changelist'))

        for field in self.list_display['page']:
            self.assertContains(response, field)

    def test_flat_page_change_fieldset(self):
        """Pages model's change-page must have all needed fields, which was define in Admin.py"""
        response = self.client.get(
            reverse(
                'se_admin:pages_flatpage_change', args=(FlatPage.objects.filter().first().id, )
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
            reverse('se_admin:shopelectro_categorypage_changelist'))

        for field in self.list_display['category']:
            self.assertContains(response, field)

    def test_category_page_change_fieldset(self):
        """
        Categories model's change-page must have all needed fields, which was define in Admin.py
        """
        response = self.client.get(
            reverse(
                'se_admin:shopelectro_categorypage_change', args=(
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
            reverse('se_admin:shopelectro_productpage_changelist'))

        for field in self.list_display['product']:
            self.assertContains(response, field)

    def test_products_change_fieldset(self):
        """Products model's change-page must have all needed fields, which was define in Admin.py"""
        response = self.client.get(
            reverse(
                'se_admin:shopelectro_productpage_change', args=(
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
        """Response should contain attr code="0" - it's mean, that all right."""
        response = self.yandex_check_request()

        self.assertContains(response, 'code="0"')
        self.assertContains(response, 'invoiceId="123"')

    def test_yandex_aviso_body(self):
        """
        Response should contain attr code="0" - it's mean, that all right, if code="1" - it's mean,
        yandex's request body contain incorrect data.
        """
        response = self.yandex_aviso_request()

        self.assertContains(response, 'code="0"')

        self.yandex_aviso_request_data['data']['md5'] = 'incorrect data'
        response = self.yandex_aviso_request()

        self.assertContains(response, 'code="1"')


class ProductsWithoutContent(TestCase):

    def test_products_without_images(self):
        response = self.client.get(reverse('products_without_images'))
        self.assertEqual(response.status_code, 200)

    def test_products_without_text(self):
        response = self.client.get(reverse('products_without_text'))
        self.assertEqual(response.status_code, 200)
