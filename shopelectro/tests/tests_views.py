"""
View tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.
"""
import json
import re
from functools import partial
from itertools import chain
from operator import attrgetter
from urllib.parse import urlparse, quote
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Count, Q
from django.http import HttpResponse
from django.test import override_settings, TestCase, tag
from django.urls import reverse
from django.utils.translation import ugettext as _

from catalog.helpers import reverse_catalog_url
from pages import models as pages_models
from pages.urls import reverse_custom_page
from shopelectro import models, views
from shopelectro.views.service import generate_md5_for_ya_kassa, YANDEX_REQUEST_PARAM

CANONICAL_HTML_TAG = '<link rel="canonical" href="{base_url}{path}">'


def get_page_number(response):
    return response.context['paginated']['page'].number


def json_to_dict(response: HttpResponse) -> dict:
    return json.loads(response.content)


class ViewsTestCase(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.category = models.Category.objects.root_nodes().select_related('page').first()
        self.tags = models.Tag.objects.order_by_alphanumeric().all()
        self.product = models.Product.objects.first()

    def get_category_url(
        self,
        category: models.Category = None,
        tags: models.TagQuerySet = None,
        sorting: int = None,
        query_string: dict = None,
        route='category',
        route_kwargs: dict = None,
    ):
        query_string = query_string or {}
        route_kwargs = route_kwargs or {}
        category = category or self.category
        route_kwargs = {
            'slug': category.page.slug,
            **route_kwargs
        }

        return reverse_catalog_url(
            route, route_kwargs, tags, sorting, query_string,
        )

    def get_category_page(self, *args, **kwargs):
        """See `self.get_category_url()` interface."""
        return self.client.get(self.get_category_url(*args, **kwargs))

    def get_product_page(self, product: models.Product=None):
        product = product or self.product
        return self.client.get(product.url)

    def get_category_soup(self, *args, **kwargs):
        return BeautifulSoup(
            self.get_category_page(*args, **kwargs).content.decode('utf-8'),
            'html.parser'
        )

    def get_product_soup(self, product: models.Product=None) -> BeautifulSoup:
        product_page = self.get_product_page(product)
        return BeautifulSoup(
            product_page.content.decode('utf-8'),
            'html.parser'
        )


@tag('fast', 'catalog')
class CatalogTags(ViewsTestCase):

    def test_category_page_contains_all_tags(self):
        """Category contains all Product's tags."""
        response = self.get_category_page()

        tags = set(chain.from_iterable(map(
            lambda x: x.tags.all(), (
                models.Product.objects
                .prefetch_related('tags')
                .filter_descendants(self.category)
            )
        )))

        tag_names = list(map(attrgetter('name'), tags))

        for tag_name in tag_names:
            self.assertContains(response, tag_name)

    def test_contains_product_with_certain_tags(self):
        """Category page contains Product's related by certain tags."""
        tags = self.tags
        response = self.get_category_page(tags=tags)

        products_count = len(list(filter(
            lambda x: x.category.is_descendant_of(self.category),
            models.Product.objects.filter(Q(tags=tags[0]) | Q(tags=tags[1]))
        )))

        self.assertEqual(
            products_count,
            response.context['paginated']['total_products']
        )
        self.assertContains(response, products_count)

    def test_tag_titles_content_disjunction(self):
        """
        Test CategoryTagsPage with canonical tags.

        CategoryTagsPage with tags "Напряжение 6В" и "Напряжение 24В"
        should contain tag_titles var content: "6В или 24В".
        """
        tag_group = models.TagGroup.objects.first()
        tags = tag_group.tags.order_by_alphanumeric().all()
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
        tag_groups = models.TagGroup.objects.order_by('position', 'name').all()
        tag_ids = [g.tags.first().id for g in tag_groups]
        tags = models.Tag.objects.filter(id__in=tag_ids)
        response = self.get_category_page(tags=tags)
        self.assertEqual(response.status_code, 200)
        delimiter = settings.TAG_GROUPS_TITLE_DELIMITER
        tag_titles = delimiter.join(t.name for t in tags)
        self.assertContains(response, tag_titles)

    def test_tags_var_in_db_template(self):
        """
        Test CategoryTagsPage with canonical tags.

        "tags" db template at CategoryTagsPage
        should render tag names. For example "1 м, 20 кг".
        """
        tags = models.Tag.objects.order_by_alphanumeric().all()
        response = self.get_category_page(tags=tags)
        self.assertEqual(response.status_code, 200)
        tag_names = ', '.join([t.name for t in tags])
        self.assertContains(response, tag_names)

    def test_product_tag_linking(self):
        """Product should contain links on CategoryTagPage for it's every tag."""
        product = models.Product.objects.first()
        self.assertGreater(product.tags.count(), 0)

        property_links = [
            reverse('category', kwargs={
                'slug': product.category.page.slug,
                'tags': tag_.slug,
            }) for tag_ in product.tags.all()
        ]
        response = self.client.get(product.url)
        for link in property_links:
            self.assertContains(response, link)

    def test_non_existing_tags_404(self):
        """Product should contain links on CategoryTagPage for it's every tag."""
        product = models.Product.objects.first()
        self.assertGreater(product.tags.count(), 0)

        bad_tag_url = reverse('category', kwargs={
            'slug': product.category.page.slug,
            'tags': 'non-existent-tag',
        })
        response = self.client.get(bad_tag_url)
        self.assertEqual(response.status_code, 404)

    def test_category_tag_relation(self):
        """Category page should contain only tags, related to the current category."""
        category = models.Category.objects.get(
            name='Category #0 of #Category #0 of #Category #0'
        )
        # category is not related to this tag at DB ...
        tag = models.Tag.objects.exclude_by_products(category.products.all()).first()
        # ... so category page should not contain this tag
        response = self.client.get(category.url)
        self.assertNotContains(response, tag.name)


@tag('fast', 'catalog')
class CatalogPagination(ViewsTestCase):

    def get_pagination_links_soup(self, page_number: int):
        return (
            self.get_category_soup(query_string={'page': page_number})
            .find(class_='js-catalog-pagination')
            .find_all('a')
        )

    def test_pagination_numbering(self):
        page_number = 1
        response = self.get_category_page(query_string={'page': page_number})
        self.assertEqual(get_page_number(response), page_number)

    def test_pagination_products_count(self):  # Ignore PyDocStyleBear
        """
        @todo #302:30m Implement test case for pagination logic.
         Products number changes in depend on page number.
         If step=24 and page number=2, then products quantity is 48.
         If step=24 and page number=2 and total products quantity is 40, then products quantity is 40.  # Ignore PycodestyleBear (E501)
        """

    def test_pagination_step(self):
        """Category page contains `pagination_step` count of products in list."""
        pagination_step = 25
        response = self.get_category_page(query_string={'step': pagination_step})
        self.assertEqual(len(response.context['paginated']['page'].object_list), pagination_step)

    def test_pagination_404(self):
        """Category page returns 404 for a nonexistent page number."""
        self.assertEqual(
            self.get_category_page(query_string={'page': 1000}).status_code,
            404,
        )

    def assert_pagination_link(self, link, page_number):
        """Page numbers from link href and from link anchor should be equal."""
        self.assertEqual(
            get_page_number(self.client.get(link['href'])),
            page_number,
        )

    def test_category_200(self):
        category_page = self.get_category_page()
        assert category_page.status_code == 200

    def test_numbered_pagination_links(self):
        """Forward to numbered pagination pages."""
        page_number = 3
        _, *numbered, _ = self.get_pagination_links_soup(page_number)
        for slice, link in zip([-2, -1, 1, 2], numbered):
            self.assert_pagination_link(link, page_number + slice)

    def test_arrow_pagination_links(self):
        """Each button forward to a previous and a next pagination pages."""
        page_number = 3
        prev, *_, next_ = self.get_pagination_links_soup(page_number)
        self.assert_pagination_link(next_, page_number + 1)
        self.assert_pagination_link(prev, page_number - 1)

    def test_pagination_canonical(self):
        """Canonical links forward to a previous and a next pagination pages."""
        page_number = 3
        soup = self.get_category_soup(query_string={'page': page_number})

        self.assert_pagination_link(
            soup.find('link', attrs={'rel': 'next'}),
            page_number + 1
        )
        self.assert_pagination_link(
            soup.find('link', attrs={'rel': 'prev'}),
            page_number - 1
        )


@tag('fast')
class LoadMore(ViewsTestCase):

    fixtures = ['dump.json']
    DEFAULT_LIMIT = 48
    PRODUCT_ID_WITH_IMAGE = 114

    def load_more(
        self,
        category: models.Category=None,
        tags: models.TagQuerySet=None,
        offset: int=0,
        # uncomment after implementation urls for load_more with pagination
        # limit: int=0,
        sorting: int=0,
        query_string: dict=None,
    ) -> HttpResponse:
        category = category or self.category
        route_kwargs = {
            'offset': offset,
            # uncomment after implementation urls for load_more with pagination
            # 'limit': limit,
        }
        return self.get_category_page(
            category=category,
            tags=tags,
            sorting=sorting,
            query_string=query_string,
            route='load_more',
            route_kwargs=route_kwargs
        )

    def get_load_more_soup(self, *args, **kwargs) -> BeautifulSoup:
        """Use interface of `self.load_more` method."""
        load_more_response = self.load_more(*args, **kwargs)
        return BeautifulSoup(
            load_more_response.content.decode('utf-8'),
            'html.parser'
        )

    def test_pagination_numbering_first_page(self):
        self.assertEqual(get_page_number(self.load_more()), 1)

    def test_pagination_numbering_last_page(self):
        offset = models.Product.objects.filter_descendants(self.category).count() - 1
        self.assertEqual(
            get_page_number(self.load_more(offset=offset)),
            offset // self.DEFAULT_LIMIT + 1,
        )

    def test_pagination_numbering_rest_page(self):
        offset = self.DEFAULT_LIMIT + 1
        self.assertEqual(
            get_page_number(self.load_more(offset=offset)),
            2,
        )

    def test_image_previews(self):
        """Load_more button should load product with image previews."""
        load_more_soup = self.get_load_more_soup(offset=self.DEFAULT_LIMIT)
        img_path = (
            load_more_soup
            .find('a', href=f'/catalog/products/{self.PRODUCT_ID_WITH_IMAGE}/')
            .find('img')['src']
        )
        self.assertNotIn('logo', img_path)


@tag('fast')
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


@tag('fast')
class RobotsPage(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.response = self.client.get('/robots.txt')

    def test_robots_success(self):
        self.assertEqual(self.response.status_code, 200)


@tag('fast')
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
        sitemap_url_slug = reverse_custom_page('sitemap')
        self.assertIn(sitemap_url_slug, self.response.content.decode('utf-8'))


@tag('fast')
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


@tag('fast', 'catalog')
class Category(ViewsTestCase):

    fixtures = ['dump.json']

    def test_page_db_template_with_special_chars(self):
        """
        DB template works with many cyrillic chars in string.

        This led to the segmentation fault issue. See #651 for details.
        """
        db_template = self.category.page.template
        db_template.seo_text = (
            '{% if page.name '
            '== "Аккумуляторы промышленные 3.7 В, Li-Pol призматические" %}'
            'some text{% else %}alt text{% endif %}'
        )
        db_template.save()
        rendered_text = db_template.render_field(
            field='seo_text',
            context={'page': self.category.page}
        )
        self.assertEqual('alt text', rendered_text)
        response = self.get_category_page()
        self.assertEqual(200, response.status_code)

    def test_canonical_meta_tag(self):
        """Category page should contain canonical meta tag."""
        path = self.get_category_url()
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            CANONICAL_HTML_TAG.format(
                base_url=settings.BASE_URL,
                path=path
            ),
        )

    def test_tags_pagination_has_canonical_links(self):
        """
        Paginated tags page should contain canonical link.

        Link on it's not paginated version.
        """
        tags = models.Tag.objects.filter_by_products(
            products=(
                models.Product.objects.all()
                .filter_descendants(self.category)
            )
        )

        not_paginated_url = self.get_category_url(
            tags=tags
        )
        paginated_url = self.get_category_url(
            tags=tags,
            query_string={'page': 2}
        )
        response = self.client.get(paginated_url)
        self.assertContains(
            response, CANONICAL_HTML_TAG.format(
                base_url=settings.BASE_URL,
                path=not_paginated_url
            )
        )

    def test_crumb_siblings_are_active(self):
        parent = models.Category.objects.annotate(c=Count('children')).filter(c__gt=1).first()
        (
            pages_models.Page.objects
            .filter(id=parent.children.first().page.id)
            .update(is_active=False)
        )
        category = parent.children.active().first()
        soup = self.get_category_soup(category.children.active().first())
        siblings = soup.select('.breadcrumbs-siblings-links a')
        self.assertFalse(
            models.Category.objects
            .filter(name__in=[s.text.strip() for s in siblings])
            .filter(page__is_active=False)
            .exists()
        )


@tag('fast', 'catalog')
class CategoriesMatrix(ViewsTestCase):

    fixtures = ['dump.json']

    def get_page(self):
        return self.client.get(
            path=reverse('custom_page', kwargs={'page': 'catalog'})
        )

    def get_soup(self) -> BeautifulSoup:
        return BeautifulSoup(
            self.get_page().content.decode('utf-8'),
            'html.parser'
        )

    def test_roots_sorting(self):
        soup = self.get_soup()
        from_page = soup.find_all('h2')
        from_db = (
            models.Category.objects.bind_fields().active()
            .filter(level=0)
            .order_by('page__position', 'name')
        ).values_list('name', flat=True)
        self.assertEqual([c.text for c in from_page], list(from_db))

    def test_second_level_sorting(self):
        soup = self.get_soup()
        from_page = soup.select('.second-level-category > a')
        from_db = (
            models.Category.objects.bind_fields().active()
            .filter(level=1)
            .order_by(
                'parent__page__position', 'parent__name',
                'page__position', 'name'
            )
        ).values_list('name', flat=True)
        self.assertEqual([c.text for c in from_page], list(from_db))


@tag('fast')
class IndexPage(TestCase):

    fixtures = ['dump.json']

    MAIN_PAGE_TILE = {
        'some_section': [
            {'name': 'Has url', 'url': '/section/first/'},
            {'name': 'Has url and slug', 'slug': 'slug', 'url': '/section/second/'},
            {'name': 'Has slug, but not url', 'slug': 'third'},
        ]
    }

    @property
    def page(self):
        return pages_models.CustomPage.objects.get(slug='')

    @override_settings(MAIN_PAGE_TILE=MAIN_PAGE_TILE)
    def test_category_tile_links(self):
        tile = views.IndexPage.get_categories_tile()
        first_url, second_url, third_url = [link['url'] for link in tile['some_section']]
        self.assertEqual('/section/first/', first_url)
        self.assertEqual('/section/second/', second_url)
        self.assertEqual('/catalog/categories/third/', third_url)

    def test_index_page_url(self):
        self.assertTrue(self.page.url)

    def test_product_tile(self):
        product = (
            models.Product.objects.active()
            .filter(id__in=settings.TOP_PRODUCTS)
            .first()
        )
        response = self.client.get(self.page.url)
        self.assertIn(product, response.context['tile_products'])
        self.assertIn(product.id, response.context['product_images'])


@tag('fast')
class ProductPage(ViewsTestCase):

    fixtures = ['dump.json']

    def test_orphan_product(self):
        self.product.category = None
        self.product.save()

        response = self.client.get(self.product.url)
        self.assertEqual(response.status_code, 404)

    def test_related_products(self):
        """404 page of sometimes removed product should contain product's siblings."""
        response = self.get_product_page()
        # 404 page should show 10 siblings. We'll check the last one
        sibling_product = self.product.category.products.all()[9]
        self.assertTrue(
            sibling_product.name in str(response.content)
        )

    def test_related_products_on_404(self):
        """404 page of some time ago removed product should contain product's siblings."""
        self.product.page.is_active = False
        self.product.save()  # saves product.page too

        response = self.get_product_page()
        # 404 page should show 10 siblings. We'll check the last one
        sibling_product = self.product.category.products.all()[9]
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            sibling_product.name in str(response.content)
        )

    def test_related_product_images(self):
        """Check previews for product's siblings on product page."""
        product_soup = self.get_product_soup(product=models.Product.objects.get(id=19))
        img_path = (
            product_soup
            .find_all(class_='stuff-top-item')[-1]
            .find('img')['src']
        )
        # app shows logo image if preview can't generated
        self.assertNotIn('logo', img_path)

    def test_page_obj(self):
        """Page object in context should be relevant to product object."""
        product = self.product
        response = self.get_product_page(product=product)
        self.assertEqual(response.context['page'], product.page)

    def test_page_contains_h1(self):
        """Page object in context should be relevant to product object."""
        product = self.product
        response = self.get_product_page(product=product)
        self.assertContains(response, product.page.display.h1)


@tag('fast')
class ProductPageSchema(TestCase):

    fixtures = ['dump.json']
    schema_url = 'https://schema.org'

    def test_available(self):
        """Page of an product with stock > 0 has $schema_url/InStock link."""
        self.assertContains(
            self.client.get(
                models.Product.objects.filter(in_stock__gt=0).first().url
            ),
            f'{self.schema_url}/InStock',
        )

    def test_not_available(self):
        """Page of an product with stock = 0 has $schema_url/PreOrder link."""
        self.assertContains(
            self.client.get(
                models.Product.objects.filter(in_stock=0).first().url
            ),
            f'{self.schema_url}/PreOrder',
        )


@tag('fast')
class ProductsWithoutContent(TestCase):

    def test_products_without_images(self):
        response = self.client.get(reverse('products_without_images'))
        self.assertEqual(response.status_code, 200)

    def test_products_without_text(self):
        response = self.client.get(reverse('products_without_text'))
        self.assertEqual(response.status_code, 200)


@tag('fast')
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
        self.assertFalse(
            list(filter(
                lambda r: r['type'] not in ['category', 'see_all'],
                json_to_dict(response),
            ))
        )

    def test_admin_autocomplete_has_no_model_pages(self):
        """Admin autocomplete does not contain page with type=MODEL_TYPE and duplicated content."""
        response = self.client.get(
            f'{reverse("admin_autocomplete")}'
            f'?term={self.QUOTED_SIGNLE_RESULT_TERM}&pageType=category'
        )
        self.assertTrue(len(json_to_dict(response)) == 1)


@tag('fast')
class Order(TestCase):

    fixtures = ['dump.json']

    def test_disabled_cache(self):
        """Cache-Control is disabled for the order page."""
        url = reverse_custom_page('order')
        self.assertEqual(
            self.client.get(url)['Cache-Control'],
            'max-age=0, no-cache, no-store, must-revalidate',
        )


@tag('fast')
class Cart(TestCase):

    fixtures = ['dump.json']

    def test_get_cart(self):
        response = self.client.get(reverse('cart_get'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json_to_dict(response))

    def test_disabled_cache(self):
        """Cache-Control is disabled for the cart-get."""
        self.assertEqual(
            self.client.get(reverse('cart_get'))['Cache-Control'],
            'max-age=0, no-cache, no-store, must-revalidate',
        )


@tag('fast', 'catalog')
class InPack(ViewsTestCase):

    fixtures = ['dump.json']

    def test_catalog_in_pack_units(self):
        category = (
            models.Category.objects
            .annotate(products_count=Count('products'))
            .filter(products__in_pack__gt=1, products_count__lt=settings.PRODUCTS_ON_PAGE_PC)
            .first()
        )

        soup = self.get_category_soup(category)
        results = soup.find_all(string=re.compile('упаковка'))

        self.assertEqual(len(results), category.products.filter(in_pack__gt=1).count(), results)

    def test_product_in_pack_units(self):
        product = models.Product.objects.filter(in_pack__gt=1).first()

        soup = self.get_product_soup(product)
        results = soup.find_all(string=re.compile('упаковка'))

        self.assertEqual(len(results), 1, results)
        self.assertIn(str(int(product.price)), results[0], results[0])
