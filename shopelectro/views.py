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
    root_categories = Category.objects.root_nodes().order_by('position')
    top_products = Product.objects.filter(is_popular=True)

    render_data = {
        'description': 'Самые низкие цены на элементы питания оптом. Доставка по России.',
        'keywords': 'аккумуляторы оптом, батарейки оптом, зарядные устройства оптом, блоки питания оптом',
        'root_categories': root_categories,
        'site_url': 'www.shopelectro.ru',
        'top': top_products,
        'title': 'Интернет магазин ShopElectro для оптовиков Санкт-Петербурга'
    }

    return render(
        request, 'shopelectro/index.html', render_data)
