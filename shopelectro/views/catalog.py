import typing
from functools import partial

from django import http
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django_user_agents.utils import get_user_agent

from catalog import newcontext
from catalog.views import catalog
from images.models import Image
from pages import views as pages_views

from shopelectro import context as se_context
from shopelectro import models
from shopelectro.views.helpers import set_csrf_cookie

PRODUCTS_ON_PAGE_PC = 48
PRODUCTS_ON_PAGE_MOB = 12


def get_products_count(request):
    """Calculate max products list size from request. List size depends on device type."""
    mobile_view = get_user_agent(request).is_mobile
    return PRODUCTS_ON_PAGE_MOB if mobile_view else PRODUCTS_ON_PAGE_PC


def get_view_type(request):
    view_type = request.session.get('view_type', 'tile')
    assert view_type in ['list', 'tile']
    return view_type


def get_catalog_context(request, category, raw_tags, page_number, per_page, sorting_index):
    all_tags = newcontext.Tags(models.Tag.objects.all())

    if raw_tags:
        selected_tags = newcontext.tags.Checked404Tags(
            newcontext.tags.ParsedTags(
                tags=all_tags,
                raw_tags=raw_tags,
            )
        )
    else:
        selected_tags = newcontext.Tags(models.Tag.objects.none())

    products = newcontext.products.OrderedProducts(
        products=newcontext.products.TaggedProducts(
            products=newcontext.products.ProductsByCategory(
                products=newcontext.products.ActiveProducts(
                    newcontext.Products(
                        models.Product.objects.all(),
                    ),
                ),
                category=category,
            ),
            tags=selected_tags,
        ),
        sorting_index=sorting_index,
    )

    paginated_products = newcontext.products.PaginatedProducts(
        products=products,
        url=request.path,
        page_number=page_number,
        per_page=per_page,
    )

    images = newcontext.products.ProductImages(paginated_products, Image.objects.all())
    brands = newcontext.products.ProductBrands(paginated_products, all_tags)
    grouped_tags = newcontext.tags.GroupedTags(all_tags)

    contexts = newcontext.Contexts(
        all_tags, paginated_products, images, brands, grouped_tags,
    )
    optional_context = {
        'skip_canonical': selected_tags.qs().exists(),
        'total_products': products.qs().count(),
        'selected_tags': selected_tags.qs(),
    }
    return contexts, optional_context


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

    @property
    def product(self):
        return self.object

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
        if not self.product.page.is_active:
            # this context required to render 404 page
            # with it's own logic
            return context_

        tile_products = self.product.get_siblings(
            offset=settings.PRODUCT_SIBLINGS_COUNT
        )
        product_images = self.get_images_context_data(tile_products)['product_images']

        return {
            **context_,
            'price_bounds': settings.PRICE_BOUNDS,
            'group_tags_pairs': self.product.get_params(),
            'product_images': product_images,
            'tile_products': tile_products,
        }

    def get_images_context_data(self, products) -> dict:
        """Return images for given products."""
        products_to_filter = [self.product, *products]
        product_ids_to_filter = [p.id for p in products_to_filter]
        return (
            se_context.ProductImages(
                url_kwargs={},
                request=self.request,
                page=self.product.page,
                products=models.Product.objects.filter(id__in=product_ids_to_filter),
                product_pages=models.ProductPage.objects.filter(
                    shopelectro_product__in=products_to_filter
                ),
            ).get_context_data()
        )

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
            siblings = inactive_product.get_siblings(
                offset=settings.PRODUCT_SIBLINGS_COUNT
            )
            self.object = inactive_product
            context_ = self.get_context_data(
                object=inactive_product,
                tile_products=siblings,
                tile_title='Возможно вас заинтересуют похожие товары:',
                **url_kwargs,
            )

            context_['product_images'] = (
                self.get_images_context_data(siblings)['product_images']
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
        top_products = (
            models.Product.objects.active()
            .filter(id__in=settings.TOP_PRODUCTS)
            .prefetch_related('category')
            .select_related('page')
        )
        if not mobile_view:
            tile_products = top_products

        return {
            **context_,
            'tile_title': 'ТОП 10 ТОВАРОВ',
            'category_tile': settings.MAIN_PAGE_TILE,
            'tile_products': tile_products,
            'product_images': (
                self.get_products_context_data(
                    products=top_products
                )['product_images']
            )
        }

    def get_products_context_data(self, products=None, product_pages=None) -> dict:
        return (
            se_context.ProductImages(
                url_kwargs={},  # Ignore CPDBear
                request=self.request,
                page=self.object,
                products=products or models.Product.objects.all(),
                product_pages=product_pages or models.ProductPage.objects.all(),
            ).get_context_data()
        )


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):

    def get_context_data(self, **kwargs):
        """Add sorting options and view_types in context."""
        sorting_index = int(self.kwargs.get('sorting', 0))

        contexts, optional_context = get_catalog_context(
            request=self.request,
            category=self.object.model,
            raw_tags=self.kwargs.get('tags'),
            page_number=int(self.request.GET.get('page', 1)),
            per_page=int(self.request.GET.get(
                'step', get_products_count(self.request),
            )),
            sorting_index=sorting_index,
        )

        selected_tags = optional_context['selected_tags']
        if selected_tags:
            def template_context(page, tag_titles, tags):
                return {
                    'page': page,
                    'tag_titles': tag_titles,
                    'tags': tags,
                }

            page = self.object
            page.get_template_render_context = partial(
                template_context, self.object, selected_tags.as_title(), selected_tags
            )

        return {
            **super().get_context_data(**kwargs),
            **contexts.context(),
            **optional_context,
            'view_type': get_view_type(self.request),
            'sorting_options': settings.CATEGORY_SORTING_OPTIONS.values(),
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
            'sort': sorting_index,
        }


def load_more(request, slug, offset=0, limit=0, sorting=0, tags=None):
    """
    Load more products of a given category.

    :param sorting: preferred sorting index from CATEGORY_SORTING tuple
    :param request: HttpRequest object
    :param slug: Slug for a given category
    :param offset: used for slicing QuerySet.
    :return: products list in html format
    """
    products_on_page = limit or get_products_count(request)
    offset = int(offset)
    if offset < 0:
        return http.HttpResponseBadRequest(
            'The offset is wrong. An offset should be greater than or equal to 0.'
        )
    # increment page number because:
    # 11 // 12 = 0, 0 // 12 = 0 but it should be the first page
    # 12 // 12 = 1, 23 // 12 = 1, but it should be the second page
    page_number = (offset // products_on_page) + 1
    category = get_object_or_404(models.CategoryPage, slug=slug).model
    sorting_index = int(sorting)

    contexts, _ = get_catalog_context(
        request=request,
        category=category,
        raw_tags=tags,
        page_number=page_number,
        per_page=products_on_page,
        sorting_index=sorting_index,
    )

    return render(request, 'catalog/category_products.html', contexts.context())


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
