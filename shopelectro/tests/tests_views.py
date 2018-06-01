"""
View tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.
"""
import json
from functools import partial
from itertools import chain
from operator import attrgetter
from xml.etree import ElementTree as ET
from urllib.parse import urlparse, quote

from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext as _

from shopelectro.models import Category, Product, Tag, TagGroup, TagQuerySet, serialize_tags_to_url
from shopelectro.views.service import generate_md5_for_ya_kassa, YANDEX_REQUEST_PARAM


CANONICAL_HTML_TAG = '<link rel="canonical" href="{path}">'


def reverse_category_url(
    category: Category, tags: TagQuerySet=None, sorting: int=None
) -> str:
    route_kwargs = {'slug': category.page.slug}

    if tags:
        # PyCharm's option:
        # noinspection PyTypeChecker
        tags_slug = serialize_tags_to_url(tags)
        route_kwargs['tags'] = tags_slug
    if sorting is not None:
        route_kwargs['sorting'] = sorting

    return reverse('category', kwargs=route_kwargs)


def json_to_dict(response: HttpResponse) -> dict():
    return json.loads(response.content)


class CatalogPage(TestCase):

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
        """Test that CategoryPage should contain canonical meta tag."""
        url = reverse_category_url(self.category)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, CANONICAL_HTML_TAG.format(path=url))

    def test_tags_page_has_no_canonical_meta_tag(self):
        """Test that CategoryTagsPage should not contain canonical meta tag."""
        # ignore CPDBear
        url = reverse_category_url(self.category, self.tags)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, CANONICAL_HTML_TAG.format(path=url))

    def test_paginated_tags_page_has_no_canonical_meta_tag(self):
        """
        Test CategoryTagsPage with canonical tags.

        CategoryTagsPage with pagination (and sorting) options
        should not contain canonical meta tag.
        """
        # ignore CPDBear
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
        Test CategoryTagsPage with canonical tags.

        CategoryTagsPage with tags "Напряжение 6В" и "Напряжение 24В"
        should contain tag_titles var content: "6В или 24В".
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
        Test CategoryTagsPage with canonical tags.

        CategoryTagsPage with tags "Напряжение 6В" и "Cила тока 1А" should
        contain tag_titles var content: "6В и 1А".
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
        Test CategoryTagsPage with canonical tags.

        CategoryTagsPage should contain "tags" template var tag=each(tags) is Tag
        class instance.
        """
        tags = Tag.objects.order_by(*settings.TAGS_ORDER).all()
        response = self.get_category_page(tags=tags)
        self.assertEqual(response.status_code, 200)
        tag_names = ', '.join([t.name for t in tags])
        self.assertContains(response, tag_names)

    def test_product_tag_linking(self):
        """Product should contain links on CategoryTagPage for it's every tag."""
        product = Product.objects.first()
        self.assertGreater(product.tags.count(), 0)

        property_links = [
            reverse('category', kwargs={
                'slug': product.category.page.slug,
                'tags': tag.slug,
            }) for tag in product.tags.all()
        ]
        response = self.client.get(product.url)
        for link in property_links:
            self.assertContains(response, link)


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


class ProductPageSchema(TestCase):

    fixtures = ['dump.json']
    schema_url = 'http://schema.org'

    def test_available(self):
        """Page of an product with stock > 0 has $schema_url/InStock link."""
        self.assertContains(
            self.client.get(
                Product.objects.filter(in_stock__gt=0).first().url
            ),
            f'{self.schema_url}/InStock',
        )

    def test_not_available(self):
        """Page of an product with stock = 0 has $schema_url/PreOrder link."""
        self.assertContains(
            self.client.get(
                Product.objects.filter(in_stock=0).first().url
            ),
            f'{self.schema_url}/PreOrder',
        )


class ProductsWithoutContent(TestCase):

    def test_products_without_images(self):
        response = self.client.get(reverse('products_without_images'))
        self.assertEqual(response.status_code, 200)

    def test_products_without_text(self):
        response = self.client.get(reverse('products_without_text'))
        self.assertEqual(response.status_code, 200)


class TestSearch(TestCase):
    """Test all search methods: search page and autocompletes."""

    fixtures = ['dump.json']
    TERM = 'Prod'
    SIGNLE_RESULT_TERM = '#0'
    QUOTED_SIGNLE_RESULT_TERM = quote(SIGNLE_RESULT_TERM)
    WRONG_TERM = 'Bugaga'  # it's short for trigram search testing

    def test_search_has_results(self):
        """Search page should contain at least one result for right term."""
        term = self.TERM
        response = self.client.get(
            f'/search/?term={term}',
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Product'))
        # search page should contain not only results.
        # But markup, menu links and so on.
        self.assertContains(response, '<title>')
        self.assertContains(response, '<div class="search-result-item">')

    def test_search_no_results(self):
        """Search page should contain no results for wrong term."""
        term = self.WRONG_TERM
        response = self.client.get(
            f'/search/?term={term}',
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<div class="search-result-item">')

    def test_autocomplete_has_results(self):
        """Autocomplete should contain at least one result for right term."""
        term = self.TERM
        response = self.client.get(
            reverse('autocomplete') + f'?term={term}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json_to_dict(response))
        self.assertContains(response, term)

    def test_autocomplete_no_results(self):
        """Autocomplete should contain no results for wrong term."""
        term = self.WRONG_TERM
        response = self.client.get(
            reverse('autocomplete') + f'?term={term}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json_to_dict(response))
        self.assertNotContains(response, term)

    def test_admin_autocomplete_has_results(self):
        """Admin autocomplete should contain at least one result for right term."""
        term = self.TERM
        page_type = 'product'
        querystring = f'?term={term}&pageType={page_type}'
        response = self.client.get(reverse('admin_autocomplete') + querystring)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json_to_dict(response))
        self.assertContains(response, term)

    def test_admin_autocomplete_no_results(self):
        """Admin autocomplete should contain no results for wrong term."""
        term = self.WRONG_TERM
        page_type = 'product'
        querystring = f'?term={term}&pageType={page_type}'
        response = self.client.get(reverse('admin_autocomplete') + querystring)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json_to_dict(response))
        self.assertNotContains(response, term)

    def test_search_has_no_model_pages(self):
        """Search page does not contain page with type=MODEL_TYPE and duplicated content."""
        response = self.client.get(
            f'/search/?term={self.QUOTED_SIGNLE_RESULT_TERM}',
            follow=True,
        )
        result_links = BeautifulSoup(
            response.content.decode('utf-8'), 'html.parser'
        ).find_all(class_='search-result-link')
        self.assertTrue(len(result_links) == 1)

    def test_autocomplete_has_no_model_pages(self):
        """Autocomplete does not contain page with type=MODEL_TYPE and duplicated content."""
        response = self.client.get(
            f'{reverse("autocomplete")}?term={self.QUOTED_SIGNLE_RESULT_TERM}'
        )
        result = list(filter(lambda d: d['type'] == 'category', json_to_dict(response)))
        self.assertTrue(
            len(result) == 1
        )

    def test_admin_autocomplete_has_no_model_pages(self):
        """Admin autocomplete does not contain page with type=MODEL_TYPE and duplicated content."""
        response = self.client.get(
            f'{reverse("admin_autocomplete")}'
            f'?term={self.QUOTED_SIGNLE_RESULT_TERM}&pageType=category'
        )
        self.assertTrue(len(json_to_dict(response)) == 1)
