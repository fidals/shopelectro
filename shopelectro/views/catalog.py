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
    Product, ProductFeedback, Category, CategoryPage as CategoryPageModel, Tag
)
from shopelectro.views.helpers import set_csrf_cookie

PRODUCTS_ON_PAGE = 48


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

        images = Image.objects.get_main_images_by_pages(top_products.get_pages())
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


def merge_products_and_images(products):
    images = Image.objects.get_main_images_by_pages(products.get_pages())

    return [
        (product, images.get(product.page))
        for product in products
    ]


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):

    def get_context_data(self, **kwargs):
        """Add sorting options and view_types in context."""
        context = super(CategoryPage, self).get_context_data(**kwargs)

        # tile is default view_type
        view_type = self.request.session.get('view_type', 'tile')

        category = context['category']

        sorting = int(self.kwargs.get('sorting', 0))
        sorting_option = config.category_sorting(sorting)

        all_products = (
            Product.objects
                .prefetch_related('page__images', 'tags', 'tags__group')
                .select_related('page')
                .get_by_category(category, ordering=(sorting_option, ))
        )

        group_tags_pairs = Tag.objects.get_group_tags_pairs(all_products.get_tags())

        tags = self.request.GET.get('tags')
        if tags:
            all_products = all_products.get_by_tags(tags.split(','))

        products = all_products.get_offset(0, PRODUCTS_ON_PAGE)

        return {
            **context,
            'product_image_pairs': merge_products_and_images(products),
            'group_tags_pairs': group_tags_pairs,
            'total_products': all_products.count(),
            'sorting_options': config.category_sorting(),
            'sort': sorting,
            'tags': tags,
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
    category_page_model = get_object_or_404(CategoryPageModel, slug=category_slug).model
    sorting_option = config.category_sorting(int(sorting))

    products = (
        Product.objects
            .prefetch_related('page__images')
            .select_related('page')
            .get_by_category(category_page_model, ordering=(sorting_option,))
    )

    tags = request.GET.get('tags')
    if tags:
        products = products.get_by_tags(tags.split(','))

    products = products.get_offset(int(offset), PRODUCTS_ON_PAGE)
    view = request.session.get('view_type', 'tile')

    return render(request, 'catalog/category_products.html', {
        'product_image_pairs': merge_products_and_images(products),
        'view_type': view,
        'prods': PRODUCTS_ON_PAGE,
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
