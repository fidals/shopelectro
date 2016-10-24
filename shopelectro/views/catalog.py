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
from shopelectro.models import (
    Product, Category, CategoryPage as CategoryPageModel)
from shopelectro.views.helpers import set_csrf_cookie


# CATALOG VIEWS
class CategoryTree(catalog.CategoryTree):
    """Override model attribute to SE-specific Category."""
    def get_context_data(self, **kwargs):
        """Add to the context correct entities."""
        context = super(CategoryTree, self).get_context_data(**kwargs)
        return {
            **context,
            'nodes': Category.objects.all()
        }


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):
    """
    Override model attribute to SE-specific Category.

    Extend get_context_data.
    """
    model = CategoryPageModel

    def get_context_data(self, **kwargs):
        """Extended method. Add sorting options and view_types."""
        context = super(CategoryPage, self).get_context_data(**kwargs)
        page = self.get_object()

        sorting = int(self.kwargs.get('sorting', 0))
        sorting_option = config.category_sorting(sorting)

        # if there is no view_type specified, default will be tile
        view_type = self.request.session.get('view_type', 'tile')

        products = Product.objects.get_products_by_category(page.model, ordering=(sorting_option, ))
        total_count = products.count()

        return {
            **context,
            'category': page.model,
            'products': products[:settings.PRODUCTS_TO_LOAD],
            'total_products': total_count,
            'sorting_options': config.category_sorting(),
            'sort': sorting,
            'view_type': view_type,
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
class IndexPage(pages_views.CustomPageView):

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
    category_page = get_object_or_404(CategoryPageModel, slug=category_slug)
    sorting_option = config.category_sorting(int(sorting))

    products = Product.objects.get_products_by_category(
        category_page.model, ordering=(sorting_option, )
    )
    view = request.session.get('view_type', 'tile')

    return render(
        request, 'catalog/category_products.html',
        {'products': products.get_offset(int(offset), 30), 'view_type': view}
    )
