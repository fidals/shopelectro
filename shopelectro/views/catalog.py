import typing
from collections import OrderedDict

from django import http
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_user_agents.utils import get_user_agent

from catalog import context
from catalog.views import catalog
from images.models import Image
# can't do `import pages` because of django error.
# Traceback: https://gist.github.com/duker33/685e8a9f59fc5dbd243e297e77aaca42
from pages import models as pages_models, views as pages_views
from shopelectro import context as se_context, models, request_data
from shopelectro.exception import Http400
from shopelectro.views.helpers import set_csrf_cookie


# block numeric indexes to limit
MATRIX_BLOCKS_TO_LIMIT = [3, 5]
MATRIX_BLOCK_SIZE = 7


# @todo #822:60m  Create tests for the catalog matrix.
#  This cases are would be good to test:
#  - Matrix sorting by page position
#  - Block items limiting
def category_matrix(request, page: str):
    assert page == 'catalog'
    roots = (
        models.Category.objects
        .bind_fields()
        .active()
        .filter(level=0)
        .order_by('page__position', 'name')
    )
    matrix = OrderedDict()
    for i, root in enumerate(roots):
        children = root.children.active()
        # @todo #822:30m  Doc category matrix blocks.
        matrix[root.name] = (
            children
            if i not in MATRIX_BLOCKS_TO_LIMIT
            else children[:MATRIX_BLOCK_SIZE]
        )
    context_ = {
        'matrix': matrix,
        'page': pages_models.CustomPage.objects.get(slug=page),
    }
    return render(request, 'catalog/catalog.html', context_)


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
        product_images = self.get_images_context_data(tile_products)

        return {
            **context_,
            **product_images,
            'group_tags_pairs': self.product.get_params().items(),
            'tile_products': tile_products,
        }

    def get_images_context_data(self, products) -> dict:
        """Return images for given products."""
        products_to_filter = [self.product, *products]
        return context.products.ProductImages(
            products_to_filter, Image.objects.all(),
        ).context()

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

            context_.update(self.get_images_context_data(siblings))
            return render(request, 'catalog/product_404.html', context_, status=404)


# SHOPELECTRO-SPECIFIC VIEWS
@set_csrf_cookie
class IndexPage(pages_views.CustomPageView):

    @staticmethod
    def get_categories_tile():
        """Patch every link with url, generated from slug."""
        return {section: [
            {**link, 'url': (
                reverse('category', kwargs={'slug': link['slug']})
                if link.get('slug') and not link.get('url')
                else link['url']
            )} for link in links
        ] for section, links in settings.MAIN_PAGE_TILE.items()}

    def get_context_data(self, **kwargs):
        """Extended method. Add product's images to context."""
        context_ = super(IndexPage, self).get_context_data(**kwargs)
        mobile_view = get_user_agent(self.request).is_mobile

        tile_products = []
        top_products = (
            models.Product.objects.active()
            .bind_fields()
            .filter(id__in=settings.TOP_PRODUCTS)
        )
        if not mobile_view:
            tile_products = top_products

        images_ctx = context.products.ProductImages(
            tile_products,
            Image.objects.all(),
        ).context()
        return {
            **context_,
            **images_ctx,
            'tile_title': 'ТОП 10 ТОВАРОВ',
            'category_tile': self.get_categories_tile(),
            'tile_products': tile_products,
        }


@set_csrf_cookie
class CategoryPage(catalog.CategoryPageTemplate):

    def get_context_data(self, **kwargs):
        """Add sorting options and view_types in context."""
        request_data_ = request_data.Catalog(self.request, self.kwargs)
        return {
            **super().get_context_data(**kwargs),
            **se_context.Catalog(request_data_).context(),
        }


def load_more(request, **url_kwargs):
    try:
        request_data_ = request_data.LoadMore(request, url_kwargs)
    except Http400:
        return http.HttpResponseBadRequest(
            'The offset is wrong. An offset should be greater than or equal to 0.'
        )
    return render(
        request,
        'catalog/category_products.html',
        se_context.Catalog(request_data_).context()
    )


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
