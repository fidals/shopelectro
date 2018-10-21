import typing

from django import http
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django_user_agents.utils import get_user_agent

from catalog import context
from catalog.views import catalog
from pages import views as pages_views

from shopelectro import models
from shopelectro.views.helpers import set_csrf_cookie

PRODUCTS_ON_PAGE_PC = 48
PRODUCTS_ON_PAGE_MOB = 12


def get_products_count(request):
    """Calculate max products list size from request. List size depends on device type."""
    mobile_view = get_user_agent(request).is_mobile
    return PRODUCTS_ON_PAGE_MOB if mobile_view else PRODUCTS_ON_PAGE_PC


# CATALOG VIEWS
class CategoryTree(catalog.CategoryTree):
    category_model = models.Category


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    pk_url_kwarg = None
    slug_url_kwarg = 'product_vendor_code'
    slug_field = 'vendor_code'

    queryset = (
        models.Product.objects.active()
        .filter(category__isnull=False)
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
        context_ = super(ProductPage, self).get_context_data(**kwargs)
        product = self.object
        if not product.page.is_active:
            # this context required to render 404 page
            # with it's own logic
            return context_

        images_context = (
            context.ProductImages(
                url_kwargs={},
                request=self.request,
                page=product.page,
                products=models.Product.objects.all(),
                product_pages=models.ProductPage.objects.all(),
            )
        )

        return {
            **context_,
            'price_bounds': settings.PRICE_BOUNDS,
            'group_tags_pairs': product.get_params(),
            'product_images': images_context.get_context_data()['product_images'],
            'tile_products': context.prepare_tile_products(
                product.get_siblings(offset=settings.PRODUCT_SIBLINGS_COUNT),
                models.ProductPage.objects.all()
            ),
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
            self.object = inactive_product
            context_ = self.get_context_data(
                object=inactive_product,
                tile_products=context.prepare_tile_products(
                    inactive_product.get_siblings(
                        offset=settings.PRODUCT_SIBLINGS_COUNT
                    ),
                    models.ProductPage.objects.all()
                ),
                tile_title='Возможно вас заинтересуют похожие товары:',
                **url_kwargs,
            )
            return render(request, 'catalog/product_404.html', context_, status=404)


# SHOPELECTRO-SPECIFIC VIEWS
@set_csrf_cookie
class IndexPage(pages_views.CustomPageView):

    def get_context_data(self, **kwargs):
        """Extended method. Add product's images to context."""
        context_ = super(IndexPage, self).get_context_data(**kwargs)
        mobile_view = get_user_agent(self.request).is_mobile

        tile_products = []
        if not mobile_view:
            top_products = (
                models.Product.objects.active()
                .filter(id__in=settings.TOP_PRODUCTS)
                .prefetch_related('category')
                .select_related('page')
            )
            tile_products = context.prepare_tile_products(
                top_products,
                models.ProductPage.objects.all()
            )

        return {
            **context_,
            'tile_title': 'ТОП 10 ТОВАРОВ',
            'category_tile': settings.MAIN_PAGE_TILE,
            'tile_products': tile_products,
        }


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):

    def get_context_data(self, **kwargs):
        """Add sorting options and view_types in context."""
        context_ = (
            context.Category(
                url_kwargs=self.kwargs,
                request=self.request,
                page=self.object,
                products=models.Product.objects.all(),
                product_pages=models.ProductPage.objects.all(),
            )
            | context.TaggedCategory(tags=models.Tag.objects.all())
            | context.ProductImages()
            | context.SortingCategory()  # requires TaggedCategory
            | context.PaginationCategory()  # requires SortingCategory
            | context.DBTemplate()  # requires TaggedCategory
        )
        return {
            **super().get_context_data(**kwargs),
            **context_.get_context_data(),
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
    sorting_option = context.SortingOption(index=int(sorting))

    all_products = models.Product.objects.active().get_category_descendants(
        category, ordering=(sorting_option.directed_field,)
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
            .distinct(sorting_option.field)
        )

    paginated = context.PaginatorLinks(
        page_number,
        request.path,
        Paginator(all_products, products_on_page)
    )
    paginated_page = paginated.page()
    products = paginated_page.object_list
    view = request.session.get('view_type', 'tile')

    context_ = (
        context.Category(
            url_kwargs={},
            request=request,
            page=category.page,
            products=models.Product.objects.all(),
            product_pages=models.ProductPage.objects.all(),
        )
        | context.ProductImages()
    )

    return render(request, 'catalog/category_products.html', {
        'products_data': context.prepare_tile_products(
            products, models.ProductPage.objects.all()
        ),
        'product_images': context_.get_context_data()['product_images'],
        'paginated': paginated,
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
