from collections import defaultdict
from copy import deepcopy
from functools import reduce
from itertools import chain
from typing import Iterator, Dict
from xml.etree.ElementTree import Element

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import QuerySet
from django.template.loader import render_to_string

from shopelectro.management.commands._update_catalog.utils import (
    XmlFile, is_correct_uuid, NOT_SAVE_TEMPLATE, UUID, Data,
)
from shopelectro.models import Product, ProductPage, Tag


def fetch_products(root: Element, config: XmlFile) -> Iterator:
    product_els = root.findall(config.xpaths['products'])

    for product_el in product_els:
        name = product_el.find(config.xpaths['name']).text
        uuid = product_el.find(config.xpaths['uuid']).text
        vendor_code = product_el.find(
            config.xpaths['vendor_code']
        ).text.lstrip('0')
        content = product_el.find(config.xpaths['content']).text

        tag_els = product_el.findall(config.xpaths['tags'])
        tag_uuids = filter(is_correct_uuid, (
            tag_el.find(config.xpaths['tag_value_uuid']).text
            for tag_el in tag_els
        ))

        tags = Tag.objects.filter(uuid__in=list(tag_uuids))

        yield uuid, {
            'name': name,
            'vendor_code': vendor_code,
            'content': content,
            'tags': tags
        }


def fetch_prices(root: Element, config) -> Iterator:
    product_price_els = root.findall(config.xpaths['product_prices'])

    def get_prices():
        def get_(price_el: Element):
            return float(price_el.find(config.xpaths['price']).text)

        return sorted(map(get_, prices_el.findall(config.xpaths['prices'])))

    for prices_el in product_price_els:
        product_uuid = prices_el.find(config.xpaths['product_uuid']).text
        prices = dict(zip(config.extra_options['price_types'], get_prices()))

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
        'content': '.{}Описание',
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
    (ex. files with product names and prices)
    """
    product_data = defaultdict(dict)
    for key, data in chain(*data):
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
            print(NOT_SAVE_TEMPLATE.format(
                entity='Product',
                name=product_data['name'],
                field='price'
            ))
        return has

    def has_vendor_code(_, product_data):
        has = bool(product_data['vendor_code'])

        if not has:
            print(NOT_SAVE_TEMPLATE.format(
                entity='Product',
                name=product_data['name'],
                field='vendor_code'
            ))

        return has

    def has_uuid(uuid, product_data):
        has = is_correct_uuid(uuid)
        if not has:
            print(NOT_SAVE_TEMPLATE.format(
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

        print('Sent message to {}'.format(
            reduce(lambda x, y: '{}, {}'.format(x, y), recipient_list)
        ))


@transaction.atomic
def delete(data: Dict[UUID, Data]):
    uuids = list(data)
    page_count, _ = ProductPage.objects.exclude(
        shopelectro_product__uuid__in=uuids).delete()
    product_count, _ = Product.objects.exclude(
        uuid__in=uuids).delete()
    print('{} products and {} pages were deleted.'.format(product_count, page_count))


@transaction.atomic
def update(data: Dict[UUID, Data]) -> QuerySet:
    def save(product, field, value):
        if field == 'name' and getattr(product, field, None):
            return
        elif field == 'content' and not getattr(product.page, field, None):
            setattr(product.page, field, value)
        else:
            setattr(product, field, value)

    products = Product.objects.filter(uuid__in=data)

    for product in products:
        product_data = data[str(product.uuid)]

        for field, value in product_data.items():
            save(product, field, value)

        product.save()
    print('{} products were updated.'.format(products.count()))
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

        new_product = Product.objects.create(**product_data, uuid=uuid)
        new_product.tags.set(tags)

    created_products = Product.objects.filter(uuid__in=uuids_for_create)

    print('{} products were created.'.format(created_products.count()))
    return created_products


def main(*args, **kwargs):
    cleaned_product_data = clean_data(merge_data(
        product_file.get_data(),
        price_file.get_data(),
        in_stock_file.get_data(),
    ))

    if not cleaned_product_data:

        parsed_files = {
            'product_files':  list(product_file.parsed_files),
            'price_files': list(price_file.parsed_files),
            'in_stock_files': list(in_stock_file.parsed_files),
        }

        if not any(parsed_files.values()):
            message = 'Files does not exist: {}'.format(parsed_files)
        else:
            # TODO: happy debugging (:
            message = 'The file structure has changed or it does not contain the required data.'

        raise Exception(message)

    delete(cleaned_product_data)
    updated_products = update(cleaned_product_data)
    created_products = create(cleaned_product_data, updated_products)

    if created_products.exists():
        report(kwargs['recipients'])
