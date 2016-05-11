"""
Basic (default) views for Catalog app.
"""

from django.shortcuts import render
from catalog.models import Category, Product
from .site_pages import get_page


def index(request):
    """
    Main page view: root categories, top products.

    :param request:
    :return: HttpResponse
    """
    root_categories = Category.objects.root_nodes().order_by('position')
    top_products = Product.objects.filter(is_popular=True)

    render_data = {
        'meta_data': get_page(page_id='main'),
        'root_categories': root_categories,
        'top': top_products,
    }

    return render(
        request, 'shopelectro/index.html', render_data)
