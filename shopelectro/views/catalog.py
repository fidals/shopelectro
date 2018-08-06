import typing
from functools import partial

from django import http
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django_user_agents.utils import get_user_agent

from catalog.views import catalog
from images.models import Image
from pages import views as pages_views

from shopelectro import config
from shopelectro import models
from shopelectro.views.helpers import set_csrf_cookie

PRODUCTS_ON_PAGE_PC = 48
PRODUCTS_ON_PAGE_MOB = 12


def get_products_count(request):
    """Calculate max products list size from request. List size depends on device type."""
    mobile_view = get_user_agent(request).is_mobile
    return PRODUCTS_ON_PAGE_MOB if mobile_view else PRODUCTS_ON_PAGE_PC


def get_paginated_page_or_404(objects, per_page, page_number):
    try:
        return Paginator(objects, per_page).page(page_number)
    except InvalidPage:
        raise http.Http404('Page does not exist')


# CATALOG VIEWS
class CategoryTree(catalog.CategoryTree):
    category_model = models.Category


def prepare_tile_products(products):
    images = Image.objects.get_main_images_by_pages(
        models.ProductPage.objects.filter(
            shopelectro_product__in=products
        )
    )
    categories = models.Category.objects.get_root_categories_by_products(
        products
    )
    return [
        (product, images.get(product.page), categories.get(product))
        for product in products
    ]


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    pk_url_kwarg = None
    slug_url_kwarg = 'product_vendor_code'
    slug_field = 'vendor_code'

    queryset = (
        models.Product.objects
        .filter(category__isnull=False, page__is_active=True)
        .prefetch_related('product_feedbacks', 'page__images')
        .select_related('page')
    )

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except http.Http404 as error404:
            response_404 = self.render_siblings_on_404(request, **kwargs)
            if response_404:
                return response_404
            else:
                raise error404

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ProductPage, self).get_context_data(**kwargs)
        product = self.object
        if not product.page.is_active:
            # this context required to render 404 page
            # with it's own logic
            return context

        group_tags_pairs = (
            models.Tag.objects
            .filter(products=self.object)
            .get_group_tags_pairs()
        )

        return {
            **context,
            'price_bounds': config.PRICE_BOUNDS,
            'group_tags_pairs': group_tags_pairs
        }

    def render_siblings_on_404(
        self, request, **url_kwargs
    ) -> typing.Union[http.Http404, None]:
        """Try to render removed product's siblings on it's 404 page."""
        inactive_product = models.Product.objects.filter(
            **{self.slug_field: url_kwargs['product_vendor_code']},
            category__isnull=False,
            page__is_active=False
        ).first()
        if inactive_product:
            related_products = (
                models.Product.objects
                .filter(
                    category=inactive_product.category,
                    page__is_active=True,
                )
                .prefetch_related('category')
                .select_related('page')[:10]
            )
            self.object = inactive_product
            context = self.get_context_data(
                object=inactive_product,
                tile_products=prepare_tile_products(related_products),
                tile_title='Возможно вас заинтересуют похожие товары:',
                **url_kwargs,
            )
            return render(request, 'catalog/product_404.html', context, status=404)


# SHOPELECTRO-SPECIFIC VIEWS
@set_csrf_cookie
class IndexPage(pages_views.CustomPageView):

    def get_context_data(self, **kwargs):
        """Extended method. Add product's images to context."""
        context = super(IndexPage, self).get_context_data(**kwargs)
        mobile_view = get_user_agent(self.request).is_mobile

        tile_products = []
        if not mobile_view:
            top_products = (
                models.Product.objects
                .filter(id__in=settings.TOP_PRODUCTS, page__is_active=True)
                .prefetch_related('category')
                .select_related('page')
            )
            tile_products = prepare_tile_products(top_products)

        return {
            **context,
            'tile_title': 'ТОП 10 ТОВАРОВ',
            'category_tile': config.MAIN_PAGE_TILE,
            'tile_products': tile_products,
        }


def merge_products_and_images(products):
    images = Image.objects.get_main_images_by_pages(
        models.ProductPage.objects.filter(shopelectro_product__in=products)
    )

    return [
        (product, images.get(product.page))
        for product in products
    ]


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):

    def get_context_data(self, **kwargs):
        """Add sorting options and view_types in context."""
        context = super().get_context_data(**kwargs)
        products_on_page = int(self.request.GET.get(
            'step', get_products_count(self.request),
        ))
        page_number = int(self.request.GET.get('page', 1))
        view_type = self.request.session.get('view_type', 'tile')
        sorting = int(self.kwargs.get('sorting', 0))
        sorting_option = config.category_sorting(sorting)
        category = context['category']
        if (
            page_number < 1 or
            products_on_page not in settings.CATEGORY_STEP_MULTIPLIERS
        ):
            raise http.Http404('Page does not exist.')  # Ignore CPDBear

        # @todo #470:15m Implement a new method for a Product's manager to get all_products
        #  as below.

        all_products = (
            models.Product.objects
            .filter(page__is_active=True)
            .prefetch_related('page__images')
            .select_related('page')
            .get_by_category(category, ordering=(sorting_option, ))
        )

        group_tags_pairs = (
            models.Tag.objects
            .filter(products__in=all_products)
            .get_group_tags_pairs()
        )

        tags = self.kwargs.get('tags')

        tag_titles = ''
        if tags:
            slugs = models.Tag.parse_url_tags(tags)
            tags = models.Tag.objects.filter(slug__in=slugs)

            all_products = (
                all_products
                .filter(tags__in=tags)
                # Use distinct because filtering by QuerySet tags,
                # that related with products by many-to-many relation.
                .distinct(sorting_option.lstrip('-'))
            )

            tag_titles = models.serialize_tags_to_title(tags)

        def template_context(page, tag_titles, tags):
            return {
                'page': page,
                'tag_titles': tag_titles,
                'tags': tags,
            }

        page = context['page']
        page.get_template_render_context = partial(
            template_context, page, tag_titles, tags)

        paginated_page = get_paginated_page_or_404(all_products, products_on_page, page_number)
        total_products = all_products.count()
        products = paginated_page.object_list
        if not products:
            raise http.Http404('Page without products does not exist.')

        return {
            **context,
            'product_image_pairs': merge_products_and_images(products),
            'group_tags_pairs': group_tags_pairs,
            'total_products': total_products,
            'products_count': (page_number - 1) * products_on_page + products.count(),
            'paginated_page': paginated_page,
            'sorting_options': config.category_sorting(),
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
            'sort': sorting,
            'tags': tags,
            'view_type': view_type,
            'skip_canonical': bool(tags),
        }


def load_more(request, category_slug, offset=0, limit=0, sorting=0, tags=None):
    """
    Load more products of a given category.

    :param sorting: preferred sorting index from CATEGORY_SORTING tuple
    :param request: HttpRequest object
    :param category_slug: Slug for a given category
    :param offset: used for slicing QuerySet.
    :return: products list in html format
    """
    products_on_page = limit or get_products_count(request)
    offset = int(offset)
    if offset < 0:
        return http.HttpResponseBadRequest(
            'The offset is wrong. An offset should be greater than or equal to 0.'
        )
    if products_on_page not in settings.CATEGORY_STEP_MULTIPLIERS:
        return http.HttpResponseBadRequest(
            'The limit number is wrong. List of available numbers:'
            f' {", ".join(map(str, settings.CATEGORY_STEP_MULTIPLIERS))}'
        )
    # increment page number because:
    # 11 // 12 = 0, 0 // 12 = 0 but it should be the first page
    # 12 // 12 = 1, 23 // 12 = 1, but it should be the second page
    page_number = (offset // products_on_page) + 1
    category = get_object_or_404(models.CategoryPage, slug=category_slug).model
    sorting_option = config.category_sorting(int(sorting))

    all_products = (
        models.Product.objects
        .filter(page__is_active=True)
        .prefetch_related('page__images')
        .select_related('page')
        .get_by_category(category, ordering=(sorting_option,))
    )

    if tags:
        tag_entities = models.Tag.objects.filter(
            slug__in=models.Tag.parse_url_tags(tags)
        )

        all_products = (
            all_products
            .filter(tags__in=tag_entities)
            # Use distinct because filtering by QuerySet tags,
            # that related with products by many-to-many relation.
            .distinct(sorting_option.lstrip('-'))
        )

    paginated_page = get_paginated_page_or_404(all_products, products_on_page, page_number)
    products = paginated_page.object_list
    view = request.session.get('view_type', 'tile')

    return render(request, 'catalog/category_products.html', {
        'product_image_pairs': merge_products_and_images(products),
        'paginated_page': paginated_page,
        'view_type': view,
        'prods': products_on_page,
    })


@require_POST
def save_feedback(request):
    def get_keys_from_post(*args):
        return {arg: request.POST.get(arg, '') for arg in args}

    product_id = request.POST.get('id')
    product = models.Product.objects.filter(id=product_id, page__is_active=True).first()
    if not (product_id and product):
        return http.HttpResponse(status=422)

    fields = ['rating', 'name', 'dignities', 'limitations', 'general']
    feedback_data = get_keys_from_post(*fields)

    models.ProductFeedback.objects.create(product=product, **feedback_data)
    return http.HttpResponse('ok')


@require_POST
def delete_feedback(request):
    if not request.user.is_authenticated:
        return http.HttpResponseForbidden('Not today, sly guy...')

    feedback_id = request.POST.get('id')
    feedback = models.ProductFeedback.objects.filter(id=feedback_id).first()
    if not (feedback_id and feedback):
        return http.HttpResponse(status=422)

    feedback.delete()
    return http.HttpResponse('Feedback with id={} was deleted.'.format(feedback_id))


class ProductsWithoutImages(catalog.ProductsWithoutImages):
    model = models.Product


class ProductsWithoutText(catalog.ProductsWithoutText):
    model = models.Product
