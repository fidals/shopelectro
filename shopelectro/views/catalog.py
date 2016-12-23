"""
Shopelectro's catalog views.

NOTE: They all should be 'zero-logic'.
All logic should live in respective applications.
"""
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from catalog.views import catalog
from images.models import Image
from pages import views as pages_views

from shopelectro import config
from shopelectro.config import PRICE_BOUNDS
from shopelectro.models import (
    Product, ProductFeedback, Category, CategoryPage as CategoryPageModel)
from shopelectro.views.helpers import set_csrf_cookie


# CATALOG VIEWS
class CategoryTree(catalog.CategoryTree):
    category_model = Category


@set_csrf_cookie
class ProductPage(catalog.ProductPage):

    queryset = (
        Product.objects
            .prefetch_related('product_feedbacks', 'page__images')
            .select_related('page')
    )

    def get_context_data(self, **kwargs):
        """Inject breadcrumbs into context."""
        context = super(ProductPage, self).get_context_data(**kwargs)
        feedbacks = (
            context[self.context_object_name]
                .product_feedbacks.all()
                .order_by('-date')
            )

        return {
            **context,
            'price_bounds': PRICE_BOUNDS,
            'feedbacks': feedbacks
        }


# SHOPELECTRO-SPECIFIC VIEWS
@set_csrf_cookie
class IndexPage(pages_views.CustomPageView):

    def get_context_data(self, **kwargs):
        """Extended method. Add product's images to context."""
        context = super(IndexPage, self).get_context_data(**kwargs)

        top_products = (
            Product.objects
                .filter(id__in=settings.TOP_PRODUCTS)
                .prefetch_related('category')
                .select_related('page')
        )

        images = Image.objects.get_main_images_by_pages(product.page for product in top_products)
        categories = Category.objects.get_root_categories_by_products(top_products)

        prepared_top_products = [
            (product, images.get(product.page), categories.get(product))
            for product in top_products
        ]

        return {
            **context,
            'category_tile': config.MAIN_PAGE_TILE,
            'prepared_top_products': prepared_top_products,
        }


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):
    PRODUCTS_ON_PAGE = 48

    def get_context_data(self, **kwargs):
        """Extended method. Add sorting options and view_types."""
        context = super(CategoryPage, self).get_context_data(**kwargs)
        category = context['category']

        sorting = int(self.kwargs.get('sorting', 0))
        sorting_option = config.category_sorting(sorting)

        # if there is no view_type specified, default will be tile
        view_type = self.request.session.get('view_type', 'tile')

        all_products = (
            Product.objects
                .prefetch_related('page__images')
                .get_by_category(category, ordering=(sorting_option, ))
                .select_related('page')
        )

        total_count = all_products.count()
        products = all_products.get_offset(0, self.PRODUCTS_ON_PAGE)
        images = Image.objects.get_main_images_by_pages(product.page for product in products)

        product_image_pairs = [
            (product, images.get(product.page))
            for product in products
        ]

        return {
            **context,
            'product_image_pairs': product_image_pairs,
            'total_products': total_count,
            'sorting_options': config.category_sorting(),
            'sort': sorting,
            'view_type': view_type,
        }


def load_more(request, category_slug, offset=0, sorting=0):
    """
    Load more products of a given category.

    :param sorting: preferred sorting index from CATEGORY_SORTING tuple
    :param request: HttpRequest object
    :param category_slug: Slug for a given category
    :param offset: used for slicing QuerySet.
    :return:
    """
    category_page = get_object_or_404(CategoryPageModel, slug=category_slug)
    sorting_option = config.category_sorting(int(sorting))

    products = (
        Product.objects
            .prefetch_related('page__images')
            .get_by_category(category_page.model, ordering=(sorting_option, ))
            .get_offset(int(offset), CategoryPage.PRODUCTS_ON_PAGE)
    )

    images = Image.objects.get_main_images_by_pages(product.page for product in products)

    product_image_pairs = [
        (product, images.get(product.page))
        for product in products
    ]

    view = request.session.get('view_type', 'tile')

    return render(request, 'catalog/category_products.html', {
        'product_image_pairs': product_image_pairs,
        'view_type': view,
        'prods': CategoryPage.PRODUCTS_ON_PAGE,
    })


@require_POST
def save_feedback(request):
    def get_keys_from_post(*args):
        return {arg: request.POST.get(arg, '') for arg in args}

    product_id = request.POST.get('id')
    product = Product.objects.filter(id=product_id).first()
    if not (product_id and product):
        return HttpResponse(status=422)

    fields = ['rating', 'name', 'dignities', 'limitations', 'general']
    feedback_data = get_keys_from_post(*fields)

    ProductFeedback.objects.create(product=product, **feedback_data)
    return HttpResponse('ok')


@require_POST
def delete_feedback(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden('Not today, sly guy...')

    feedback_id = request.POST.get('id')
    feedback = ProductFeedback.objects.filter(id=feedback_id).first()
    if not (feedback_id and feedback):
        return HttpResponse(status=422)

    feedback.delete()
    return HttpResponse('Feedback with id={} was deleted.'.format(feedback_id))


class ProductsWithoutImages(catalog.ProductsWithoutImages):
    model = Product


class ProductsWithoutText(catalog.ProductsWithoutText):
    model = Product
