from functools import reduce

from django.core.management.base import BaseCommand
from django.db import transaction

from shopelectro.models import ProductPage, CategoryPage, Product


CATEGORY_TITLE = '{name} - купить в интернет-магазине - ShopElectro'
CATEGORY_TITLE_WITH_PRICE = '''
{name} - купить в интернет-магазине в СПб оптом, цена от {price:.0f} руб -
ShopElectro
'''.replace('\n', ' ')

CATEGORY_SEO_TEXT_POSTFIX = '''
Наши цены ниже, чем у конкурентов, потому что мы покупаем напрямую у
производителя.
'''.replace('\n', ' ').strip()

PRODUCT_TITLE = '''
{name} - купить недорого оптом, со скидкой в интернет-магазине ShopElectro
в СПб, цена - {price:.0f} руб
'''.replace('\n', ' ')

PRODUCT_DESCRIPTION = '''
{name} - Элементы питания, зарядные устройства, ремонт. Купить
{category_name} в Санкт-Петербурге.
'''.replace('\n', ' ')


def update_category_title(page_):
    product_with_lowest_price = (
        Product.objects
        .get_by_category(page_.model)
        .order_by('price').first()
    )
    page_.title = (
        CATEGORY_TITLE_WITH_PRICE.format(
            name=page_.name,
            price=product_with_lowest_price.price,
        ) if product_with_lowest_price
        else CATEGORY_TITLE.format(name=page_.name)
    )
    return page_


def update_category_text(page_):
    category_text = page_.seo_text.strip()

    if 'Наши цены' not in category_text:  # so dirty
        page_.seo_text = ' '.join([
            category_text, CATEGORY_SEO_TEXT_POSTFIX,
        ])
    else:
        idx = category_text.index('Наши цены')
        if idx > 0:
            page_.seo_text = ' '.join([
                category_text[:idx - 1], CATEGORY_SEO_TEXT_POSTFIX,
            ])
        else:
            page_.seo_text = CATEGORY_SEO_TEXT_POSTFIX

    return page_


def update_product_title(page_):
    page_.title = PRODUCT_TITLE.format(
        name=page_.name,
        price=page_.model.price,
    )
    return page_


def update_product_description(page_):
    category_name = (
        page_.model.category.name
        if page_.model.category else ''
    )
    page_.description = PRODUCT_DESCRIPTION.format(
        name=page_.name,
        category_name=category_name
    )
    return page_


@transaction.atomic
def chained_update(pages, handlers):
    def handle(handlers_, page_):
        result_page = reduce(lambda x, y: y(x), handlers_, page_)
        result_page.save()

    for page in pages.iterator():
        handle(handlers, page)

    print('Updated {} meta tags'.format(
        pages[0].model._meta.verbose_name_plural
    ))


def update():
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

    chained_update(
        category_pages,
        handlers=[
            update_category_title,
            update_category_text,
        ]
    )
    chained_update(
        product_pages,
        handlers=[
            update_product_title,
            update_product_description,
        ]
    )


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        update()
