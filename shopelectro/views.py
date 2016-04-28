"""
Basic (default) views for Catalog app.
"""

from django.shortcuts import render
from catalog.models import Category, Product


def index(request):
    """
    Main page view: root categories, top products.

    :param request:
    :return: HttpResponse
    """
    roots = Category.objects.root_nodes()
    top_products = Product.objects.filter(is_popular=True)

    return render(
        request, 'shopelectro/main.html', {'roots': roots, 'top': top_products})