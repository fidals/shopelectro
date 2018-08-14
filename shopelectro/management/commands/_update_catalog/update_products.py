import logging
import typing
from collections import defaultdict
from copy import deepcopy
from functools import reduce
from itertools import chain
from typing import Dict, Iterator, List
from xml.etree.ElementTree import Element

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import QuerySet
from django.template.loader import render_to_string

from shopelectro.management.commands._update_catalog.utils import (
    XmlFile, is_correct_uuid, NOT_SAVE_TEMPLATE, UUID, Data, floor
)
from shopelectro.models import Product, ProductPage, Tag


logger = logging.getLogger(__name__)


def fetch_products(root: Element, config: XmlFile) -> Iterator:
    product_els = root.findall(config.xpaths['products'])
    for product_el in product_els:
        name = product_el.find(config.xpaths['name']).text
        uuid = product_el.find(config.xpaths['uuid']).text
        vendor_code = product_el.find(
            config.xpaths['vendor_code']
        ).text.lstrip('0')
        content = product_el.find(config.xpaths['page_content']).text or ''

        tag_value_els = (
            tag_el.find(config.xpaths['tag_value_uuid'])
            for tag_el in product_el.findall(config.xpaths['tags'])
            if tag_el is not None
        )

        tag_uuids = list(filter(is_correct_uuid, (
            tag_value.text
            for tag_value in tag_value_els
            # should use 'is not None', because __bool__ does not defined
            if tag_value is not None
        )))

        tags = Tag.objects.filter(uuid__in=tag_uuids)

        yield uuid, {
            'name': name,
            'vendor_code': vendor_code,
            'page': {
                'content': content
            },
            'tags': tags
        }


def fetch_prices(root: Element, config) -> typing.Iterator:
    def get_price_values(prices_el):
        return list(sorted(
            float(price_el.find(config.xpaths['price']).text)
            for price_el in prices_el.findall(config.xpaths['prices'])
        ))

    def multiply(prices: typing.List[float]):
        def floor_prices(prices, precision: floor):
            return [
                floor(price * multiplier, precision)
                for price, multiplier in zip(prices, settings.PRICE_MULTIPLIERS)
            ]
        *wholesale_prices, retail_price = prices
        return (
            floor_prices(wholesale_prices, precision=2) +
            floor_prices([retail_price], precision=0)
        )

    product_price_els = root.findall(config.xpaths['product_prices'])
    for prices_el in product_price_els:
        product_uuid = prices_el.find(config.xpaths['product_uuid']).text
        prices = dict(zip(
            config.extra_options['price_types'],
            multiply(get_price_values(prices_el))
        ))
        yield product_uuid, prices


def fetch_in_stock(root: Element, config: XmlFile) -> Iterator:
    product_els = root.findall(config.xpaths['products'])
    for product_el in product_els:
        uuid = product_el.find(config.xpaths['product_uuid']).text
        in_stock = product_el.find(config.xpaths['in_stock']).text

        if not (in_stock.isdigit() and int(in_stock) >= 0):
            in_stock = 0

        yield uuid, {
            'in_stock': in_stock,
        }


product_file = XmlFile(
    fetch_callback=fetch_products,
    xml_path_pattern='**/webdata/**/goods/**/import*.xml',
    xpath_queries={
        'products': './/{}Товары/',
        'name': '.{}Наименование',
        'uuid': '.{}Ид',
        'page_content': '.{}Описание',
        'tags': '.{}ЗначенияСвойств/',
        'tag_value_uuid': '.{}Значение',
        'vendor_code': '.{0}ЗначенияРеквизитов/{0}ЗначениеРеквизита'
                       '[{0}Наименование="Код"]/{0}Значение',
    },
)

price_file = XmlFile(
    fetch_callback=fetch_prices,
    xml_path_pattern='**/webdata/**/goods/**/prices*.xml',
    xpath_queries={
        'product_prices': './/{}Предложения/',
        'product_uuid': '.{}Ид',
        'prices': '.{}Цены/',
        'price': '.{}ЦенаЗаЕдиницу',
    },
    extra_options={
        'price_types': [
            'purchase_price', 'wholesale_large', 'wholesale_medium',
            'wholesale_small', 'price',
        ],
    },
)


in_stock_file = XmlFile(
    fetch_callback=fetch_in_stock,
    xml_path_pattern='**/webdata/**/goods/**/rests*.xml',
    xpath_queries={
        'products': './/{}Предложения/',
        'product_uuid': '.{}Ид',
        'in_stock': './/{}Количество',
    },
)


def merge_data(*data) -> Dict[UUID, Data]:
    """
    Merge data from xml files with different structure.

    Example: files with product names and prices.
    """
    product_data = defaultdict(dict)
    for key, data in chain.from_iterable(filter(None, data)):
        product_data[key].update(data)

    return product_data


def clean_data(data: Dict[UUID, Data]):
    def has_all_prices(_, product_data):
        price_types = price_file.extra_options['price_types']
        has = all(
            product_data.get(price_type)
            for price_type in price_types
        )
        if not has:
            logger.info(NOT_SAVE_TEMPLATE.format(
                entity='Product',
                name=product_data['name'],
                field='price'
            ))
        return has

    def has_vendor_code(_, product_data):
        has = bool(product_data['vendor_code'])

        if not has:
            logger.info(NOT_SAVE_TEMPLATE.format(
                entity='Product',
                name=product_data['name'],
                field='vendor_code'
            ))

        return has

    def has_uuid(uuid, product_data):
        has = is_correct_uuid(uuid)
        if not has:
            logger.info(NOT_SAVE_TEMPLATE.format(
                entity='Product',
                name=product_data['name'],
                field='uuid'
            ))
        return has

    def filter_(product_data):
        return all(
            f(*product_data)
            for f in [has_all_prices, has_uuid, has_vendor_code]
        )

    cleaned_data = dict(
        product_data
        for product_data in data.items()
        if filter_(product_data)
    )

    return cleaned_data


def report(recipients=None, message=None):
    message = message or render_to_string('report.html')

    user_query = (
        User.objects
            .filter(is_staff=True, is_superuser=False, is_active=True, email__isnull=False)
    )

    recipient_list = recipients or [user.email for user in user_query]

    if recipient_list:
        send_mail(
            subject='Обновления каталога товаров',
            message=message,
            from_email=settings.EMAIL_SENDER,
            recipient_list=recipient_list,
            html_message=message,
        )

        logger.info('Sent message to {}'.format(
            reduce(lambda x, y: '{}, {}'.format(x, y), recipient_list)
        ))


@transaction.atomic
def delete(data: Dict[UUID, Data]):
    uuids = list(data)
    pages_to_deactivate = ProductPage.objects.exclude(
        shopelectro_product__uuid__in=uuids)
    pages_to_deactivate.update(is_active=False)
    deactivated_count = pages_to_deactivate.count()
    logger.info(f'{deactivated_count} products and {deactivated_count} pages were deleted.')


@transaction.atomic
def update(data: Dict[UUID, Data]) -> QuerySet:
    def save(product, field, value):
        if field == 'name' and getattr(product, field, None):
            return
        elif field == 'page':
            for page_field, page_value in value.items():
                if not getattr(product.page, page_field, ''):
                    setattr(product.page, page_field, page_value)
        else:
            setattr(product, field, value)

    def merge(left: List, right: List) -> List:
        """Merge two arrays with order preserving."""
        return left + [e for e in right if e not in left]

    products = Product.objects.filter(uuid__in=data)

    for product in products:
        product_data = data[str(product.uuid)]
        for field, value in product_data.items():
            if field != 'tags':
                save(product, field, value)
            else:
                # Dirty patch for preserving tags, appended from admin.
                # Still waiting 1C throwing out.
                product.tags = merge(list(product.tags.all()), value)

        product.save()
    logger.info('{} products were updated.'.format(products.count()))
    return products


@transaction.atomic
def create(data: Dict[UUID, Data], updated_products: QuerySet) -> QuerySet:
    data = deepcopy(data)
    uuids_for_create = (
        set(data) - set(str(product.uuid) for product in updated_products)
    )

    for uuid in uuids_for_create:
        product_data = data.get(uuid)
        tags = product_data.pop('tags', {})
        page_data = product_data.pop('page', {})

        new_product = Product.objects.create(**product_data, uuid=uuid)
        new_product.tags.set(tags)
        for field, value in page_data.items():
            setattr(new_product.page, field, value)
        new_product.page.save()

    created_products = Product.objects.filter(uuid__in=uuids_for_create)

    logger.info('{} products were created.'.format(created_products.count()))
    return created_products


class UpdateProductError(Exception):
    pass


def main(*args, **kwargs):
    cleaned_product_data = clean_data(merge_data(
        product_file.get_data(),
        price_file.get_data(),
        in_stock_file.get_data(),
    ))

    if not cleaned_product_data:

        parsed_files = {
            'product_files': list(product_file.parsed_files),
            'price_files': list(price_file.parsed_files),
            'in_stock_files': list(in_stock_file.parsed_files),
        }

        if not any(parsed_files.values()):
            message = 'Files does not exist: {}'.format(parsed_files)
        else:
            # file structure is unstable.
            # You should adapt code for it if you got this error
            message = (
                'The file structure has changed'
                ' or it does not contain the required data.'
            )

        raise UpdateProductError(message)

    delete(cleaned_product_data)
    updated_products = update(cleaned_product_data)
    created_products = create(cleaned_product_data, updated_products)

    if created_products.exists():
        report(kwargs['recipients'])
