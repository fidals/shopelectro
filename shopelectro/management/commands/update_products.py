from collections import defaultdict
from contextlib import contextmanager
from functools import reduce
import glob
from itertools import chain
import os
import shutil
import subprocess
from typing import Iterator, Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from django.db import transaction
from django.db.models import QuerySet
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from shopelectro.models import Product, ProductPage

ProductUUID = str
ProductData = Dict[str, str]

NAMESPACE = '{urn:1C.ru:commerceml_2}'


@contextmanager
def download_catalog(destination):
    """
    Download catalog's xml files and delete after handle them.
    """
    wget_command = (
        'wget -r -P {} ftp://{}:{}@{}/webdata'
        ' 2>&1 | grep "время\|time\|Downloaded"'.format(
            destination,
            settings.FTP_USER,
            settings.FTP_PASS,
            settings.FTP_IP,
        )
    )

    subprocess.run(wget_command, shell=True, check=True)
    print('Download catalog - completed...')

    try:
        yield
    finally:
        # remove downloaded data
        shutil.rmtree(os.path.join(destination, settings.FTP_IP))


def get_xpath_queries(namespace: str, queries: Dict[str, str]) -> Dict[str, str]:
    """Insert the namespace prefix to queries."""
    return {
        name: query.format(namespace)
        for name, query in queries.items()
    }


def fetch_name(root: Element, xpath_queries: Dict[str, str]) -> Iterator:
    product_els = root.findall(xpath_queries['products'])
    for product_el in product_els:
        product_name = product_el.find(xpath_queries['product_name']).text
        product_uuid = product_el.find(xpath_queries['product_uuid']).text
        yield product_uuid, {'name': product_name}


def fetch_price(root: Element, xpath_queries: Dict[str, str], **kwargs) -> Iterator:
    product_price_els = root.findall(xpath_queries['product_prices'])

    def get_prices():
        def get_(price_el: Element):
            return float(price_el.find(xpath_queries['price']).text)

        return sorted(map(get_, prices_el.findall(xpath_queries['prices'])))

    for prices_el in product_price_els:
        product_uuid = prices_el.find(xpath_queries['product_uuid']).text

        prices = dict(zip(
            kwargs['price_types'],
            get_prices()
        ))

        yield product_uuid, prices

PRODUCT_NAME_CONFIG = {
    'fetch_callback': fetch_name,
    'xml_path_pattern': os.path.join(
        settings.ASSETS_DIR,
        '**/webdata/**/goods/**/import*.xml',
    ),
    'xpath_queries': get_xpath_queries(
        NAMESPACE,
        {
            'products': './/{}Товары/',
            'product_uuid': '.{}Ид',
            'product_name': '.{}Наименование',
        },
    ),
}

PRODUCT_PRICE_CONFIG = {
    'fetch_callback': fetch_price,
    'xml_path_pattern': os.path.join(
        settings.ASSETS_DIR,
        '**/webdata/**/goods/**/prices*.xml',
    ),
    'xpath_queries': get_xpath_queries(
        NAMESPACE,
        {
            'product_prices': './/{}Предложения/',
            'product_uuid': '.{}Ид',
            'prices': '.{}Цены/',
            'price': '.{}ЦенаЗаЕдиницу',
        }),
    'price_types': [
        'purchase_price', 'wholesale_large', 'wholesale_medium',
        'wholesale_small', 'price',
    ],
}


def get_data(
        xpath_queries: Dict[str, str], xml_path_pattern: str,
        fetch_callback: callable, **kwargs
) -> Iterator:
    """
    Get data from xml files, that matched the path pattern.
    (ex. files with products names or prices)
    """
    return chain.from_iterable(
        fetch_callback(ElementTree.parse(path), xpath_queries, **kwargs)
        for path in glob.glob(xml_path_pattern)
    )


def merge_data(*data) -> Dict[ProductUUID, ProductData]:
    """
    Merge data from xml files with different structure.
    (ex. files with product names and prices)
    """
    product_data = defaultdict(dict)
    for key, data in chain(*data):
        product_data[key].update(data)

    return product_data


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipients',
            nargs='+',
            default=[],
            help='Send an email to recipients if products will be created.',
        )

    def handle(self, *args, **kwargs):
        with download_catalog(destination=settings.ASSETS_DIR):
            cleaned_product_data = self.clean_data(self.get_product_data())

            if not cleaned_product_data:
                raise Exception('Problem with uploaded files.')

            self.delete(cleaned_product_data)
            updated_products = self.update(cleaned_product_data)
            created_products = self.create(cleaned_product_data, updated_products)

            if created_products.exists():
                self.report(kwargs['recipients'])

    @staticmethod
    def get_product_data() -> Dict[ProductUUID, ProductData]:
        return merge_data(
            get_data(**PRODUCT_NAME_CONFIG),
            get_data(**PRODUCT_PRICE_CONFIG)
        )

    @staticmethod
    def clean_data(data: Dict[ProductUUID, ProductData]):
        def has_all_prices(product_data_: ProductData):
            price_types = PRODUCT_PRICE_CONFIG['price_types']
            has_them = all(map(lambda x: product_data_.get(x) is not None, price_types))
            if not has_them:
                template = 'Product with name="{}" has no price. It\'ll not be saved'
                print(template.format(product_data_['name']))
            return has_them

        cleaned_data = {
            uuid: product_data
            for uuid, product_data in data.items()
            if has_all_prices(product_data)
        }

        return cleaned_data

    @staticmethod
    def report(recipients=None):
        message = render_to_string('report.html')

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
    def delete(self, data: Dict[ProductUUID, ProductData]):
        products = Product.objects.exclude(uuid__in=data)
        page_count, _ = ProductPage.objects.filter(shopelectro_product__in=products).delete()
        product_count, _ = products.delete()
        print('{} products  and {} pages were deleted.'.format(product_count, page_count))

    @transaction.atomic
    def update(self, data: Dict[ProductUUID, ProductData]) -> QuerySet:
        products = Product.objects.filter(uuid__in=data.keys())
        for product in products:
            product_data = data[str(product.uuid)]
            for field, value in product_data.items():
                setattr(product, field, value)

            product.save()
        print('{} products were updated.'.format(products.count()))
        return products

    @transaction.atomic
    def create(self, data: Dict[ProductUUID, ProductData], updated_products: QuerySet) -> QuerySet:
        uuids_for_create = (
            set(data.keys()) - set(str(product.uuid) for product in updated_products)
        )

        for uuid in uuids_for_create:
            product_data = data.get(uuid)
            Product.objects.create(**product_data, uuid=uuid)
        created_products = Product.objects.filter(uuid__in=uuids_for_create)

        print('{} products were created.'.format(created_products.count()))
        return created_products
