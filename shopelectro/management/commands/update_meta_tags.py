from functools import reduce

from django.db import transaction
from django.core.management.base import BaseCommand

from shopelectro.models import ProductPage, CategoryPage, Product

CATEGORY_TITLE = '{0.name} - купить в интернет-магазине - ShopElectro'
CATEGORY_TITLE_WITH_PRICE = '''
{0.name} - купить в интернет-магазине в СПб оптом, цена от {1.price:.0f} -
ShopElectro
'''.replace('\n', ' ')

CATEGORY_SEO_TEXT_POSTFIX = '''
Наши цены ниже, чем у конкурентов, потому что мы покупаем напрямую у
производителя.
'''.replace('\n', ' ')

PRODUCT_TITLE = '''
{0.name} - купить недорого оптом, со скидкой в интернет-магазине ShopElectro
в СПб, цена - {0.model.price:.0f}.
'''.replace('\n', ' ')

PRODUCT_DESCRIPTION = '''
{0.name} - Элементы питания, зарядные устройства, ремонт. Купить
{0.model.category.name} в Санкт-Петербурге.
'''.replace('\n', ' ')


def get_category_handlers():
    def update_title(page_):
        category_products = Product.objects.get_by_category(page_.model)
        if category_products.exists():
            product_with_lowest_price = category_products.order_by('price').first()
            page_.title = CATEGORY_TITLE_WITH_PRICE.format(
                page_, product_with_lowest_price,
            )
        else:
            page_.title = CATEGORY_TITLE.format(page_)
        return page_

    def update_seo_text(page_):
        if CATEGORY_SEO_TEXT_POSTFIX not in page_.seo_text.strip():
            page_.seo_text = '{} {}'.format(
                page_.seo_text, CATEGORY_SEO_TEXT_POSTFIX,
            )
        return page_

    return update_title, update_seo_text


def get_product_handlers():
    def update_title(page_):
        page_.title = PRODUCT_TITLE.format(page_)
        return page_

    def update_description(page_):
        page_.description = PRODUCT_DESCRIPTION.format(page_)
        return page_

    return update_title, update_description


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        category_pages = (
            CategoryPage.objects
                .select_related('shopelectro_category')
                .prefetch_related('shopelectro_category__products')
        )

        product_pages = (
            ProductPage.objects
                .select_related('shopelectro_product')
                .prefetch_related('shopelectro_product__category')
        )

        self.update(product_pages, get_product_handlers())
        self.update(category_pages, get_category_handlers())

    @transaction.atomic
    def update(self, pages, handlers):
        def handle(functions, arg):
            processed_page = reduce(lambda x, y: y(x), functions, arg)
            processed_page.save()

        for page in pages.iterator():
            handle(handlers, page)

        print('Updated {} meta tags'.format(
            pages[0].model._meta.verbose_name_plural
        ))
