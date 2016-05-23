"""
Shopelectro views.

NOTE: They all should be 'zero-logic'. All logic should live in respective applications.
"""

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from catalog.models import Category, Product, get_crumbs
from . import config


def index(request):
    """
    Main page view: root categories, top products.

    :param request:
    :return: HttpResponse
    """
    top_products = Product.objects.filter(id__in=config.TOP_PRODUCTS)

    context = {
        'meta_data': config.page_metadata('main'),
        'category_tile': config.MAIN_PAGE_TILE,
        'footer_links': config.FOOTER_LINKS,
        'href': config.HREFS,
        'top_products': top_products,
    }

    return render(
        request, 'index/index.html', context)


def category_page(request, category_slug, sorting=0):
    """
    Category page: all it's subcategories and products.

    :param sorting: preferred sorting index from CATEGORY_SORTING tuple
    :param category_slug: given category's slug
    :param request: HttpRequest object
    :return:
    """
    sorting = int(sorting)
    sorting_option = config.category_sorting(sorting)

    # if there is no view_type specified, default will be tile
    view_type = request.session.get('view_type', 'tile')
    category = get_object_or_404(Category.objects, slug=category_slug)
    products, total_count = category.get_recursive_products_with_count(
        sorting=sorting_option)

    context = {'category': category,
               'products': products,
               'total_products': total_count,
               'sorting_options': config.category_sorting(),
               'sort': sorting,
               'breadcrumbs': get_crumbs(category),  # chosen sorting option
               'view_type': view_type}

    return render(request, 'catalog/category.html', context)


def load_more(request, category_slug, offset=0, sorting=0):
    """
    Loads more products of a given category.

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

    return render(request, 'catalog/category_products.html',
                  {'products': products, 'view_type': view})


@require_POST
def set_view_type(request):
    """
    Simple 'view' for setting view type to user's session.
    Requires POST HTTP method, since it sets data to session.

    :param request:
    :return:
    """
    request.session['view_type'] = request.POST['view_type']
    return HttpResponse('ok')  # Return 200 OK
