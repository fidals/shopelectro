"""
Contains view context classes.

Context is our own concept.
It's part of the View abstract layer in MTV paradigm.
Data flow looks like this:
Urls -> Context -> View.
So, by concept, View receives context directly
without accessing url args.
It stands between urls and view functions.

Every context class is used via objects composition.
Code example to create tagged category:

>>> from django.http import HttpRequest
>>> url_kwargs = {'slug': 'my-page'}
>>> Category(url_kwargs, request=HttpRequest()) | TaggedCategory()
"""

import typing
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import lru_cache, partial

from django import http
from django.conf import settings
from django.db.models import QuerySet
from django.core.paginator import Paginator, InvalidPage
from django_user_agents.utils import get_user_agent

from catalog.models import ProductQuerySet, Tag, TagQuerySet
from images.models import Image
from pages.models import ModelPage

from shopelectro import models


class SortingOption:
    def __init__(self, index=0):
        options = settings.CATEGORY_SORTING_OPTIONS[index]
        self.label = options['label']
        self.field = options['field']
        self.direction = options['direction']

    @property
    def directed_field(self):
        return self.direction + self.field


class PaginatorLinks:

    def __init__(self, number, path, paginated: Paginator):
        self.paginated = paginated
        self.number = number
        self.path = path

        self.index = number - 1
        self.neighbor_bounds = settings.PAGINATION_NEIGHBORS // 2
        self.neighbor_range = list(self.paginated.page_range)

    def page(self):
        try:
            return self.paginated.page(self.number)
        except InvalidPage:
            raise http.Http404('Page does not exist')

    def showed_number(self):
        return self.index * self.paginated.per_page + self.page().object_list.count()

    def _url(self, number):
        self.paginated.validate_number(number)
        return self.path if number == 1 else f'{self.path}?page={number}'

    def prev_numbers(self):
        return self.neighbor_range[:self.index][-self.neighbor_bounds:]

    def next_numbers(self):
        return self.neighbor_range[self.index + 1:][:self.neighbor_bounds]

    def number_url_map(self):
        numbers = self.prev_numbers() + self.next_numbers()
        return {number: self._url(number) for number in numbers}


# @todo #550:30m Split to ProductImagesContext and ProductBrandContext
@lru_cache(maxsize=64)
def prepare_tile_products(
    products: ProductQuerySet, product_pages: QuerySet=None, tags: TagQuerySet=None
):
    # @todo #550:60m Move prepare_tile_products func to context
    #  Now it's separated function with huge of inconsistent queryset deps.
    assert isinstance(products, ProductQuerySet)

    product_pages = product_pages or models.ProductPage.objects.all()
    images = Image.objects.get_main_images_by_pages(
        product_pages.filter(shopelectro_product__in=products)
    )

    tags = tags or models.Tag.objects.all()
    brands = (
        tags
        .filter_by_products(products)
        .get_brands(products)
    ) if tags else defaultdict(lambda: None)

    return [
        (product, images.get(product.page), brands.get(product))
        for product in products
    ]


class ObjectsComposition:

    super: 'ObjectsComposition' = None

    def __or__(self, other: 'ObjectsComposition'):
        other.super = self
        return other


# @todo #550:120m Move context realization to pure to objects composition.
#  Discussed some thoughts with Artemiy via call.
#  Artemiy will do it.
#  For example SortedCategory should
#  consist of separated SortedList and Category classes/objects.
class AbstractContext(ObjectsComposition, ABC):

    super: 'AbstractContext' = None

    def __init__(  # Ignore PyDocStyleBear
        self,
        url_kwargs: typing.Dict[str, str]=None,
        request: http.HttpRequest=None
    ):
        """
        :param url_kwargs: Came from `urls` module.
        :param request: Came from `urls` module
        """

        self.url_kwargs_ = url_kwargs or {}
        self.request_ = request

    @property
    def url_kwargs(self) -> typing.Dict[str, str]:
        return self.url_kwargs_ or self.super.url_kwargs

    @property
    def request(self) -> http.HttpRequest:
        return self.request_ or self.super.request

    @abstractmethod
    def get_context_data(self) -> typing.Dict[str, typing.Any]:
        ...


class AbstractPageContext(AbstractContext, ABC):

    super: 'AbstractPageContext' = None

    def __init__(  # Ignore PyDocStyleBear
        self,
        url_kwargs: typing.Dict[str, str]=None,
        request: http.HttpRequest=None
    ):
        """
        :param url_kwargs: Came from `urls` module.
        :param request: Came from `urls` module
        """

        if url_kwargs:
            assert 'slug' in url_kwargs
        super().__init__(url_kwargs, request)

    @property
    def slug(self) -> str:
        return self.url_kwargs['slug']

    @property
    @lru_cache(maxsize=1)
    def page(self):
        return ModelPage.objects.get(slug=self.slug)


class AbstractProductsListContext(AbstractPageContext, ABC):

    super: 'AbstractProductsListContext' = None

    def __init__(  # Ignore PyDocStyleBear
        self,
        url_kwargs: typing.Dict[str, str]=None,
        request: http.HttpRequest=None,
        products: ProductQuerySet=None,
        product_pages: QuerySet=None,
    ):
        """
        :param url_kwargs: Came from `urls` module.
        :param request: Came from `urls` module.
        :param products: Every project provides products from DB.
        """
        super().__init__(url_kwargs, request)
        self.products_ = products
        self.product_pages_ = product_pages


    @property
    def product_pages(self) -> QuerySet:
        return self.product_pages_ or self.super.product_pages

    @property
    def products(self) -> ProductQuerySet:
        if self.super:
            return self.super.products
        elif self.products_:
            return self.products_
        else:
            raise NotImplementedError('Set products queryset')


class Category(AbstractProductsListContext):
    @property
    def products(self) -> ProductQuerySet:
        return super().products.active().get_category_descendants(
            self.page.model
        )

    def get_context_data(self):
        """Add sorting options and view_types in context."""
        # @todo #550:15m Take `view_type` value from dataclass.
        #  Depends on updating to python3.7
        view_type = self.request.session.get('view_type', 'tile')

        return {
            'products_data': prepare_tile_products(self.products, self.product_pages),
            # can be `tile` or `list`. Defines products list layout.
            'view_type': view_type,
        }


class TaggedCategory(AbstractProductsListContext):

    def __init__(  # Ignore PyDocStyleBear
        self,
        url_kwargs: typing.Dict[str, str]=None,
        request: http.HttpRequest=None,
        products: ProductQuerySet=None,
        tags: TagQuerySet=None
    ):
        """
        :param url_kwargs: Came from `urls` module.
        :param request: Came from `urls` module.
        :param products: Every project provides products from DB.
        :param tags: Every project provides tags from DB.
        """
        super().__init__(url_kwargs, request, products)
        # it's not good. Arg should not be default.
        # That's how we'll prevent assertion.
        # But we'll throw away inheritance in se#567.
        assert tags, 'tags is required arg'
        self.tags_ = tags

    def get_sorting_index(self):
        return int(self.url_kwargs.get('sorting', 0))

    # TODO - move to property as in `products` case
    def get_tags(self) -> typing.Optional[TagQuerySet]:
        request_tags = self.url_kwargs.get('tags')
        if not request_tags:
            return None

        slugs = Tag.parse_url_tags(request_tags)
        tags = self.tags_.filter(slug__in=slugs)
        if not tags:
            raise http.Http404('No such tag.')
        return tags

    @property
    def products(self):
        products = self.super.products
        sorting_option = SortingOption(index=self.get_sorting_index())
        tags = self.get_tags()
        if tags:
            products = (
                products
                .filter(tags__in=tags)
                # Use distinct because filtering by QuerySet tags,
                # that related with products by many-to-many relation.
                # @todo #550:60m Try to rm sorting staff from context.TaggedCategory.
                #  Or explain again why it's impossible. Now it's not clear from comment.
                .distinct(sorting_option.field)
            )
        return products

    def get_context_data(self):
        context = self.super.get_context_data()
        tags = self.get_tags()
        group_tags_pairs = (
            self.tags_
            .filter_by_products(self.products)
            .get_group_tags_pairs()
        )
        return {
            **context,
            'tags': tags,
            'group_tags_pairs': group_tags_pairs,
            'products_data': prepare_tile_products(
                self.products,
                self.product_pages,
                # requires all tags, not only selected
                self.tags_
            ),
            # Category's canonical link is `category.page.get_absolute_url`.
            # So, this link always contains no tags.
            # That's why we skip canonical link on tagged category page.
            'skip_canonical': bool(tags),
        }


class DBTemplate(AbstractPageContext):
    """Processes some page data fields as templates with their own context."""

    @property
    @lru_cache(maxsize=1)
    def page(self):
        page = self.super.page
        context = self.get_super_context_data_cached()

        def template_context(page, tag_titles, tags):
            return {
                'page': page,
                'tag_titles': tag_titles,
                'tags': tags,
            }

        tags = context['tags']
        if tags:
            tag_titles = tags.as_title()
            page.get_template_render_context = partial(
                template_context, page, tag_titles, tags
            )

        return page

    @lru_cache(maxsize=1)
    def get_super_context_data_cached(self):
        return self.super.get_context_data()

    @lru_cache(maxsize=1)
    def get_context_data(self):
        return {
            **self.get_super_context_data_cached(),
            'page': self.page,
        }


class SortingCategory(AbstractProductsListContext):

    def get_sorting_index(self):
        return int(self.url_kwargs.get('sorting', 0))

    @property
    def products(self) -> ProductQuerySet:
        sorting_index = int(self.url_kwargs.get('sorting', 0))
        sorting_option = SortingOption(index=sorting_index)
        return self.super.products.order_by(sorting_option.directed_field)

    def get_context_data(self):
        context = self.super.get_context_data()
        return {
            **context,
            'products_data': prepare_tile_products(self.products),
            'sort': self.get_sorting_index(),
        }


class PaginationCategory(AbstractProductsListContext):

    def get_products_count(self):
        """Calculate max products list size from request. List size depends on device type."""
        mobile_view = get_user_agent(self.request).is_mobile
        return settings.PRODUCTS_ON_PAGE_MOB if mobile_view else settings.PRODUCTS_ON_PAGE_PC

    # TODO - reload self.products
    def get_paginated_page_or_404(self, per_page, page_number) -> Paginator:
        try:
            return Paginator(self.all_products, per_page).page(page_number)
        except InvalidPage:
            raise http.Http404('Page does not exist')

    @property
    def products_on_page(self):
        return int(self.request.GET.get(
            'step', self.get_products_count(),
        ))

    @property
    def page_number(self):
        return int(self.request.GET.get('page', 1))

    @property
    def all_products(self) -> ProductQuerySet:
        return self.super.products

    @property
    def products(self) -> ProductQuerySet:
        """Only products for current page."""
        paginated_page = self.get_paginated_page_or_404(
            self.products_on_page, self.page_number
        )
        # it's queryset, but it's sliced
        products: ProductQuerySet = paginated_page.object_list
        return products

    @property
    def products_count(self):
        return (self.page_number - 1) * self.products_on_page + self.products.count()

    def check_pagination_args(self):
        if (
            self.page_number < 1 or
            self.products_on_page not in settings.CATEGORY_STEP_MULTIPLIERS
        ):
            raise http.Http404('Page does not exist.')  # Ignore CPDBear

    def get_context_data(self):
        context = self.super.get_context_data()
        self.check_pagination_args()

        if not self.products:
            raise http.Http404('Page without products does not exist.')

        paginated = PaginatorLinks(
            self.page_number,
            self.request.path,
            Paginator(self.all_products, self.products_on_page)
        )
        paginated_page = paginated.page()

        total_products = self.all_products.count()

        return {
            **context,
            'products_data': prepare_tile_products(self.products),
            'total_products': total_products,
            'products_count': self.products_count,
            'paginated': paginated,
            'paginated_page': paginated_page,
            'sorting_options': settings.CATEGORY_SORTING_OPTIONS.values(),
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
        }
