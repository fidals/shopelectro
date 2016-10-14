"""
Shopelectro's catalog views.

NOTE: They all should be 'zero-logic'.
All logic should live in respective applications.
"""
from django.shortcuts import render, get_object_or_404
from django.conf import settings

from pages import views as pages_views
from catalog.views import catalog

from shopelectro import config
from shopelectro.models import Product, Category
from shopelectro.views.helpers import set_csrf_cookie


# CATALOG VIEWS
class CategoryTree(catalog.CategoryTree):
    """Override model attribute to SE-specific Category."""
    model = Category


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):
    """
    Override model attribute to SE-specific Category.

    Extend get_context_data.
    """
    model = Category

    def get_context_data(self, **kwargs):
        """Extended method. Add sorting options and view_types."""
        context = super(CategoryPage, self).get_context_data(**kwargs)
        category = self.get_object()

        sorting = int(self.kwargs.get('sorting', 0))
        sorting_option = config.category_sorting(sorting)

        # if there is no view_type specified, default will be tile
        view_type = self.request.session.get('view_type', 'tile')
        products, total_count = (
            category.get_recursive_products_with_count(sorting=sorting_option)
        )

        return {
            **context,
            'products': products,
            'total_products': total_count,
            'sorting_options': config.category_sorting(),
            'sort': sorting,
            'view_type': view_type,
            'page': category.page,
        }


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    """
    Override model attribute to SE-specific Product.

    Extend get_context_data.
    """
    model = Product

    def get_context_data(self, **kwargs):
        """Extended method. Add product's images to context.."""
        context = super(ProductPage, self).get_context_data(**kwargs)
        product = self.get_object()

        return {
            **context,
            'page': product.page,
        }


# SHOPELECTRO-SPECIFIC VIEWS
@set_csrf_cookie
class IndexPage(pages_views.IndexPage):

    def get_context_data(self, **kwargs):
        """Extended method. Add product's images to context."""
        context = super(IndexPage, self).get_context_data(**kwargs)

        top_products = Product.objects.filter(id__in=settings.TOP_PRODUCTS)

        return {
            **context,
            'category_tile': config.MAIN_PAGE_TILE,
            'top_products': top_products,
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

    category = get_object_or_404(Category.objects, slug=category_slug)
    sorting_option = config.category_sorting(int(sorting))
    products, _ = category.get_recursive_products_with_count(
        sorting=sorting_option, offset=int(offset))
    view = request.session.get('view_type', 'tile')

    return render(
        request, 'catalog/category_products.html',
        {'products': products, 'view_type': view}
    )
