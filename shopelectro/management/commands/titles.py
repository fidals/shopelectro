"""
This command generate seo titles for products and categories
"""

from django.core.management.base import BaseCommand
from shopelectro.models import Category, Product


CATEGORY_TITLE = '{name} купить в интернет-магазине - ShopElectro'
CATEGORY_TITLE_WITH_PRICE = '{name} купить в интернет-магазине, цена от {price} руб - ShopElectro'

PRODUCT_TITLE = '''
    {name} - купить недорого, со скидкой в интернет-магазине ShopElectro, цена - {price} руб
'''

PRODUCT_DESCRIPTION = '''
    {name} - Купить.
    {category_name} в Санкт Петербурге.
'''


def update_categories():
    def get_min_price(category: Category):
        """Get min price among Category's Products."""
        min_product = (
            Product.objects
            .filter(category=category)
            .order_by('price').first()
        )
        return int(min_product.price) if min_product else 0

    for category in Category.objects.all():
        page = category.page
        min_price = get_min_price(category)
        page.title = (
            CATEGORY_TITLE_WITH_PRICE.format(
                name=page.name, price=min_price
            ) if min_price
            else CATEGORY_TITLE.format(name=page.name)
        )
        page.save()


def update_products():
    for product in Product.objects.all():
        page = product.page

        category = product.category
        page.title = PRODUCT_TITLE.format(name=page.name, price=int(product.price))
        if not page.description:
            page.description = PRODUCT_DESCRIPTION.format(
                name=page.name, category_name=category.name
            )
        page.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_categories()
        update_products()
