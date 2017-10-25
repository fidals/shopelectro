"""
View tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.
"""
from functools import partial
from itertools import chain
from operator import attrgetter
from xml.etree import ElementTree as ET
from urllib.parse import urlparse

from django.conf import settings
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse

from shopelectro.models import Category, Product, Tag, TagGroup, TagQuerySet
from shopelectro.views.service import generate_md5_for_ya_kassa, YANDEX_REQUEST_PARAM


CANONICAL_HTML_TAG = '<link rel="canonical" href="{path}">'


def reverse_category_url(
    category: Category, tags: TagQuerySet=None, sorting: int=None
) -> str:
    route_kwargs = {'slug': category.page.slug}

    if tags:
        # PyCharm's option:
        # noinspection PyTypeChecker
        tags_slug = Tag.serialize_url_tags(tags.get_group_tags_pairs())
        route_kwargs['tags'] = tags_slug
    if sorting is not None:
        route_kwargs['sorting'] = sorting

    return reverse('category', kwargs=route_kwargs)


class CategoryPage(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.category = Category.objects.root_nodes().select_related('page').first()
        self.tags = Tag.objects.order_by(*settings.TAGS_ORDER).all()

    def get_category_page(self, category=None, tags=None):
        category = category or self.category
        return self.client.get(reverse_category_url(category, tags))

    def test_category_page_contains_all_tags(self):
        """Category contains all Product's tags."""
        response = self.client.get(reverse('category', args=(self.category.page.slug, )))

        tags = set(chain.from_iterable(map(
            lambda x: x.tags.all(), Product.objects.get_by_category(self.category)
        )))

        tag_names = list(map(attrgetter('name'), tags))

        for tag_name in tag_names:
            self.assertContains(response, tag_name)

    def test_has_canonical_meta_tag(self):
        """CategoryPage should contain canonical meta tag"""
        url = reverse_category_url(self.category)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, CANONICAL_HTML_TAG.format(path=url))

    def test_tags_page_has_no_canonical_meta_tag(self):
        """CategoryTagsPage should not contain canonical meta tag"""
        url = reverse_category_url(self.category, self.tags)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, CANONICAL_HTML_TAG.format(path=url))

    def test_paginated_tags_page_has_no_canonical_meta_tag(self):
        """
        CategoryTagsPage with pagination (and sorting) options
        should not contain canonical meta tag
        """
        url = reverse_category_url(self.category, self.tags, sorting=1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, CANONICAL_HTML_TAG.format(path=url))

    def test_contains_product_with_certain_tags(self):
        """Category page contains Product's related by certain tags."""
        tags = self.tags
        response = self.get_category_page(tags=tags)

        products_count = len(list(filter(
            lambda x: x.category.is_descendant_of(self.category),
            Product.objects.filter(Q(tags=tags[0]) | Q(tags=tags[1]))
        )))

        self.assertContains(response, products_count)

    def test_tag_titles_content_disjunction(self):
        """
        CategoryTagsPage with tags "Напряжение 6В" и "Напряжение 24В"
        should contain tag_titles var content: "6В или 24В"
        """
        tag_group = TagGroup.objects.first()
        tags = tag_group.tags.order_by(*settings.TAGS_ORDER).all()
        response = self.get_category_page(tags=tags)
        self.assertEqual(response.status_code, 200)
        delimiter = settings.TAGS_TITLE_DELIMITER
        tag_titles = delimiter.join(t.name for t in tags)
        self.assertContains(response, tag_titles)

    def test_tag_titles_content_conjunction(self):
        """
        CategoryTagsPage with tags "Напряжение 6В" и "Cила тока 1А"
        should contain tag_titles var content: "6В и 1А"
        """
        tag_groups = TagGroup.objects.order_by('position', 'name').all()
        tag_ids = [g.tags.first().id for g in tag_groups]
        tags = Tag.objects.filter(id__in=tag_ids)
        response = self.get_category_page(tags=tags)
        self.assertEqual(response.status_code, 200)
        delimiter = settings.TAG_GROUPS_TITLE_DELIMITER
        tag_titles = delimiter.join(t.name for t in tags)
        self.assertContains(response, tag_titles)

    def test_tags_var(self):
        """
        CategoryTagsPage should contain "tags" template var
        tag=each(tags) is Tag class instance
        """
        tags = Tag.objects.order_by(*settings.TAGS_ORDER).all()
        response = self.get_category_page(tags=tags)
        self.assertEqual(response.status_code, 200)
        tag_names = ', '.join([t.name for t in tags])
        self.assertContains(response, tag_names)


class SitemapXML(TestCase):
    """
    Test Sitemap XML.

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
        path = '{0}url[2]/{0}loc'.format(self.NAMESPACE)
        model_url_text = urlparse(self.root.find(path).text).path
        response = self.client.get(model_url_text)

        self.assertEqual(response.status_code, 200)


class SitemapPage(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.response = self.client.get('/sitemap/')

    def test_pagination_on_page(self):
        paginator_pages = list(self.response.context['paginator_pages'])
        paginator_links = self.response.context['paginator_links']

        self.assertTrue(len(paginator_pages) == 50)
        self.assertFalse(len(paginator_links) == 0)

    def test_sitemap_self_link_on_page(self):
        sitemap_url_slug = reverse('custom_page', args=('sitemap', ))
        self.assertIn(sitemap_url_slug, self.response.content.decode('utf-8'))


class YandexKassa(TestCase):
    """
    Test yandex check order and yandex aviso.

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
        Test response code.

        Response should contain attr code="0" - it's mean, that all right,
        if code="1" - it's mean, yandex's request body contain incorrect data.
        """
        response = self.yandex_aviso_request()

        self.assertContains(response, 'code="0"')

        self.yandex_aviso_request_data['data']['md5'] = 'incorrect data'
        response = self.yandex_aviso_request()

        self.assertContains(response, 'code="1"')


class ProductPage(TestCase):

    fixtures = ['dump.json']

    def test_orphan_product(self):
        product = Product.objects.first()
        product.category = None
        product.save()

        response = self.client.get(product.url)
        self.assertEqual(response.status_code, 404)


class ProductsWithoutContent(TestCase):

    def test_products_without_images(self):
        response = self.client.get(reverse('products_without_images'))
        self.assertEqual(response.status_code, 200)

    def test_products_without_text(self):
        response = self.client.get(reverse('products_without_text'))
        self.assertEqual(response.status_code, 200)
