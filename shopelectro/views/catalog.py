import typing

from django import http
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_user_agents.utils import get_user_agent

from catalog import newcontext
from catalog.views import catalog
from images.models import Image
from pages import views as pages_views
from shopelectro import models, context as se_context
from shopelectro.views.helpers import set_csrf_cookie


# TODO - place this context and RequestData to separated modules.
class ListParamsContext(newcontext.Context):

    def __init__(self, request_data: 'ProductListRequestData'):
        self.request_data = request_data

    def context(self) -> dict:
        return {
            'view_type': self.request_data.get_view_type(),
            'sorting_options': settings.CATEGORY_SORTING_OPTIONS.values(),
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
            'sort': self.request_data.sorting_index,
        }


class CatalogContext(newcontext.Context):
    def __init__(self, request_data: 'ProductListRequestData', category, page):
        self.request_data = request_data
        self.category = category
        self.page = page

    @staticmethod
    def get_all_tags() -> newcontext.Tags:
        return newcontext.Tags(models.Tag.objects.all())

    def select_tags(self) -> newcontext.tags.ParsedTags:
        selected_tags = newcontext.tags.ParsedTags(
            tags=self.get_all_tags(),
            raw_tags=self.request_data.tags,
        )
        if self.request_data.tags:
            selected_tags = newcontext.tags.Checked404Tags(selected_tags)
        return selected_tags

    def filter_products(self) -> newcontext.Products:
        return newcontext.products.OrderedProducts(
            sorting_index=self.request_data.sorting_index,
            products=newcontext.products.TaggedProducts(
                tags=self.select_tags(),
                products=newcontext.products.ProductsByCategory(
                    category=self.category,
                    products=newcontext.products.ActiveProducts(
                        newcontext.Products(
                            models.Product.objects.all(),
                        ),
                    ),
                )
            ),
        )

    def paginate_products(self) -> newcontext.products.PaginatedProducts:
        """
        We have to use separated method for pagination,
        because paginated QuerySet can not used as QuerySet.
        It's not the most strong place of Django ORM, of course.

        :return: ProductsContext with paginated QuerySet inside
        """
        # @todo #683:30m Remove *Tags and *Products suffixes from catalog.newcontext classes.
        #  Rename Checked404Tags to ExistingOr404.
        paginated_products = newcontext.products.PaginatedProducts(
            products=self.filter_products(),
            url=self.request_data.request.path,
            page_number=self.request_data.pagination_page_number,
            per_page=self.request_data.pagination_per_page,
        )
        return paginated_products

    def context(self) -> dict:
        images = newcontext.products.ProductImages(self.paginate_products(), Image.objects.all())
        brands = newcontext.products.ProductBrands(self.paginate_products(), self.get_all_tags())
        grouped_tags = newcontext.tags.GroupedTags(
            tags=newcontext.tags.TagsByProducts(self.get_all_tags(), self.filter_products().qs())
        )
        page = se_context.Page(self.page, self.select_tags())
        product_list = ListParamsContext(self.request_data)

        # TODO - pass category, children, etc

        return newcontext.Contexts(
            page, self.paginate_products(),
            images, brands, grouped_tags, product_list
        ).context()


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
        product_images = self.get_images_context_data(tile_products)

        return {
            **context_,
            **product_images,
            'price_bounds': settings.PRICE_BOUNDS,
            'group_tags_pairs': self.product.get_params(),
            'tile_products': tile_products,
        }

    def get_images_context_data(self, products) -> dict:
        """Return images for given products."""
        products_to_filter = [self.product, *products]
        return newcontext.products.ProductImages(
            newcontext.Products(products_to_filter),
            Image.objects.all(),
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
            .filter(id__in=settings.TOP_PRODUCTS)
            .prefetch_related('category')
            .select_related('page')
        )
        if not mobile_view:
            tile_products = top_products

        images_ctx = newcontext.products.ProductImages(
            newcontext.Products(tile_products),
            Image.objects.all(),
        ).context()
        return {
            **context_,
            **images_ctx,
            'tile_title': 'ТОП 10 ТОВАРОВ',
            'category_tile': self.get_categories_tile(),
            'tile_products': tile_products,
        }


class RequestData:
    def __init__(
        self, request: http.HttpRequest, url_kwargs: typing.Dict[str, str]
    ):
        self.request = request
        self.url_kwargs = url_kwargs


class ProductListRequestData(RequestData):
    """Data came from django urls to django views."""

    PRODUCTS_ON_PAGE_PC = 48
    PRODUCTS_ON_PAGE_MOB = 12
    VIEW_TYPES = ['list', 'tile']

    @property
    def sorting_index(self):
        return int(self.url_kwargs.get('sorting', 0))

    @property
    def tags(self) -> str:
        """Tags list in url args format."""
        return self.url_kwargs.get('tags')

    @property
    def length(self):
        """Max products list size based on device type."""
        is_mobile = get_user_agent(self.request).is_mobile
        return (
            self.PRODUCTS_ON_PAGE_MOB
            if is_mobile else self.PRODUCTS_ON_PAGE_PC
        )

    def get_view_type(self):
        view_type = self.request.session.get('view_type', 'tile')
        assert view_type in self.VIEW_TYPES
        return view_type

    @property
    def pagination_page_number(self):
        return int(self.request.GET.get('page', 1))

    @property
    def pagination_per_page(self):
        return int(self.request.GET.get('step', self.length))


# @todo #723:60m  Create separated PaginationRequestData class.
#  And may be remove `LoadMoreRequestData` class.
class LoadMoreRequestData(ProductListRequestData):

    @property
    def offset(self):
        return int(self.url_kwargs.get('offset', 0))

    @property
    def pagination_page_number(self):
        # increment page number because:
        # 11 // 12 = 0, 0 // 12 = 0 but it should be the first page
        # 12 // 12 = 1, 23 // 12 = 1, but it should be the second page
        return (self.offset // self.pagination_per_page) + 1


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):

    def get_context_data(self, **kwargs):
        """Add sorting options and view_types in context."""
        request_data = ProductListRequestData(self.request, self.kwargs)
        context_ = CatalogContext(
            request_data,
            page=self.object,
            category=self.object.model,
        )
        return {
            **super().get_context_data(**kwargs),
            **context_.context(),
        }


def load_more(request, **url_kwargs):
    request_data = LoadMoreRequestData(request, url_kwargs)
    if request_data.offset < 0:
        return http.HttpResponseBadRequest(
            'The offset is wrong. An offset should be greater than or equal to 0.'
        )
    page = get_object_or_404(models.CategoryPage, slug=url_kwargs['slug'])
    context_ = CatalogContext(
        request_data,
        page=page,
        category=page.model,
    )
    return render(request, 'catalog/category_products.html', context_.context())


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
