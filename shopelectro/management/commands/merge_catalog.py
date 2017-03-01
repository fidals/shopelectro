"""Should be executed only once."""

from collections import defaultdict
import os
from typing import Iterator, Dict
import time
from xml.etree.ElementTree import Element

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import transaction, connection

from pages.models import Page

from shopelectro.management.commands import update_products as xml_command
from shopelectro.models import Category, Product

CategoryUUID = int
CategoryData = xml_command.ProductData

CATEGORY_UUID_ID_MAP = {
    'ec5c4037-530c-4dde-baa2-302785ec8300': 2,
    '81e387cb-721e-4670-ab21-9a8e29aea18a': 3,
    '1171cf37-a548-4bdc-80ea-153ec0652e6a': 4,
    'ff16f8f4-254a-4454-90b2-f9f3eb0e4c29': 6,
    '44cb88b3-0af2-45e3-80ce-8d4f48ea2085': 7,
    'a97673a6-3920-456c-8100-82bd5e060837': 11,
    '7a41a918-d602-48cc-bffb-d1797ab4d069': 12,
    '1146f7ae-70e8-4512-b8d9-be26226bbbbe': 13,
    '64d70c3c-6eef-4021-9577-06169213e174': 18,
    '61a2ccb6-7037-46d7-b3fc-6a95f7c5af03': 19,
    '37c41c13-2558-4c0f-a52d-1daca13899de': 22,
    '4cf1ed3d-4ed7-458d-9e58-a7c7739e453e': 24,
    'afe6f9f6-df2a-49d7-8148-47d1c943eec1': 25,
    '5ae52594-b61d-4ac9-820b-346c562751d6': 26,
    'ee4cd14b-8c3c-4f6d-9c6c-462f5a8a357b': 27,
    '60aa57ef-c42e-4619-b896-4347164a2313': 29,
    '55a840b6-167d-4c98-a698-eef1856bafea': 30,
    '3e58df7d-24f9-47ff-9816-8220b60cc042': 31,
    '7887fbf9-1741-4665-b27f-2a74f1bd8e26': 32,
    'd8f44ac6-5064-4b70-b130-d83690cf6de4': 33,
    '7604d495-e757-4535-ab13-337ddd98b572': 34,
    '6840f668-299e-4204-ad80-e92c1747892a': 35,
    'e2f12275-df92-4047-a906-4ecb2002754b': 36,
    'aa91cf81-cf86-4d6c-9288-d28c2820d7ac': 37,
    'b0dfc1f5-0c47-441a-ba0a-d0894321d36d': 39,
    'b086fde0-48fd-47be-ab90-54df8ad1d494': 41,
    'ef35b0ce-3bda-40ca-981d-2ec7e6733deb': 43,
    'b7408819-c726-45d5-8a13-6de254745488': 44,
    '8cdb9a14-d2b3-4e4b-b514-d06e0779c0c4': 45,
    '66dd893c-32e7-4284-89d9-2fa4dd123177': 46,
    '3469e0c5-451f-4603-b6ef-01b68bfd95c7': 47,
    '1491bc3d-dbb6-40ed-beaa-a9d7e75640a6': 50,
    '498a94d6-828f-41de-ae86-1b1388416f9f': 51,
    '6ab9cbce-0664-435e-b335-074ae4269b6f': 52,
    '58a3a37f-06e3-4b6e-a21e-29e7c69d0d84': 53,
    '2784ecdb-77a0-4aed-90ff-2b465a00f75c': 54,
    '7b02df0e-7ea0-4ed4-ae4c-74b570339af8': 63,
    '14705c1f-cb7e-4601-8d55-00f649efb2be': 71,
    'c916b538-a068-4de8-b228-c136a53b1837': 81,
    '1e731bc5-2dc9-4c7b-bbd6-c4768999f273': 104,
    '8354390d-95be-4220-af94-f2c2ff26d108': 111,
    'ba78e050-5332-4a97-8ef8-ef7bcd369738': 112,
    '2f118862-7c70-4269-a219-b47e93ac5495': 121,
    '8e28f737-f856-4286-ad58-5a7b6e0848dd': 124,
    '6511559d-60b4-4f52-8b16-07a1c5d1f707': 125,
    '3ff24b94-c66c-484b-bad3-fe402947eebf': 126,
    '0d1b5b1e-11a9-430e-99bd-2d6187183bf3': 127,
    '7ba3e2e5-2f1b-4c30-9791-2c42223fb57d': 128,
    'ea499e59-3ed2-44f4-91d8-9be9e257705d': 129,
    '94da3cdb-f232-4b22-b2c9-71ea21067029': 130,
    '402e43d0-e860-49ff-b513-ec0f798c3117': 141,
    '652dd743-7c51-42a9-a63f-42b0f7dee940': 142,
    '37398c4b-e77b-4516-a1e1-1547a80f1bb4': 143,
    'aa5e214d-f8c3-4dd0-a2bc-238f9e97342d': 144,
    '6abacb1f-844d-4322-9fa8-612a05c13ad4': 145,
    'd5240761-70a7-4c28-9abe-27a76137643c': 147,
    '03a0dac8-9b94-45b5-9a70-98f1bd11b26e': 149,
    '07ac08fd-35dc-4cf5-b25e-9f3bd49be0ad': 150,
    '622020cd-b06e-4da1-b5a1-67ea66a659ef': 151,
    'e5a459ae-8f92-4ece-a215-f113945e5c41': 152,
    'e251ba4e-a821-4b01-9c9c-7de41cd50796': 153,
    '234555f9-a04a-487d-af8d-a1173b9d1b61': 155,
    '5ec73e91-0565-4739-8141-38c113b67418': 156,
    'e0093aa2-8654-4a08-aa0e-90c5cad654ad': 157,
    '4875f0a2-305f-4876-ac29-d5b7e16902c6': 158,
    '674df7ff-d5ac-42ad-b215-7733e7f01335': 160,
    'f19c9aa3-b13a-47f6-8fa2-89406eb62f89': 168,
    'dc470a39-7495-4cf8-b92f-2574e9611bed': 169,
    '9d48a801-14e2-4997-9062-079e3dae5381': 172,
    'aee6090d-7414-4c0a-a49a-730a26bada1c': 192,
    '190ad518-cfa3-4700-b033-1f5ea576de7c': 195,
    'd069618b-5e09-47ed-b38a-b72b93027f16': 203,
}


def fetch_product_data(root: Element, xpath_queries: Dict[str, str]) -> Iterator:
    product_els = root.findall(xpath_queries['products'])

    for product_el in product_els:
        product_id = product_el.find(xpath_queries['product_id']).text.lstrip('0')
        product_uuid = product_el.find(xpath_queries['product_uuid']).text
        category_uuid = product_el.find(xpath_queries['category_uuid']).text
        yield category_uuid, {product_id: product_uuid}


def fetch_category_data(root: Element, xpath_queries: Dict[str, str]) -> Iterator:
    category_els = root.findall(xpath_queries['categories'])

    def fetch(el):
        category_uuid = el.find(xpath_queries['category_uuid']).text
        category_name = el.find(xpath_queries['category_name']).text
        children_el = el.findall(xpath_queries['category_children'])
        category_children = dict(map(fetch, children_el))
        return category_uuid, {
            'name': category_name, 'children': category_children, 'products_data': {},
        }

    for category_el in category_els:
        yield fetch(category_el)


PRODUCT_CONFIG = {
    'fetch_callback': fetch_product_data,
    'xml_path_pattern': xml_command.PRODUCT_NAME_CONFIG['xml_path_pattern'],
    'xpath_queries': xml_command.get_xpath_queries(
        xml_command.NAMESPACE, {
            'products': './/{}Товары/',
            'product_uuid': '.{}Ид',
            'product_id': './/{0}ЗначениеРеквизита/[{0}Наименование="Код"]/{0}Значение',
            'category_uuid': '.{}Группы/',
        },
    ),
}

CATEGORY_CONFIG = {
    'fetch_callback': fetch_category_data,
    'xml_path_pattern': os.path.join(
        settings.ASSETS_DIR,
        '**/webdata/**/import*.xml'
    ),
    'xpath_queries': xml_command.get_xpath_queries(
        xml_command.NAMESPACE, {
            'categories': '.{0}Классификатор/{0}Группы/',
            'category_uuid': '.{}Ид',
            'category_name': '.{}Наименование',
            'category_children': '.{}Группы/',
        },
    ),
}


def merge_data(category_data: Iterator, product_data: Iterator) -> Dict[CategoryUUID, CategoryData]:
    """Merge xml files' data"""
    new_product_data = defaultdict(dict)
    for category_uuid, data in product_data:
        new_product_data[category_uuid].update(data)

    def merge_(category_data_):
        merged_data = category_data_.copy()
        for uuid in merged_data:
            if uuid in new_product_data:
                merged_data[uuid]['products_data'] = new_product_data[uuid]

            if merged_data[uuid]['children']:
                merged_data[uuid]['children'] = merge_(
                    merged_data[uuid]['children'],
                )

        return merged_data

    return merge_(dict(category_data))


@transaction.atomic
def merge_catalog(category_data: Dict[CategoryUUID, CategoryData]):
    page_fields = ['keywords', 'description', 'content', 'position', 'seo_text']
    se_site = Site.objects.get(domain=settings.SITE_DOMAIN_NAME)

    categories_on_delete = [category.id for category in Category.objects.all()]
    old_redirects_count = Redirect.objects.count()

    def merge_meta_data(old_category_, new_category_):
        for field in page_fields:
            setattr(new_category_.page, field, getattr(old_category_.page, field))
        new_category_.page.save()

    def create_redirects(old_category_, new_category_):
        if not old_category_.url == new_category_.url:
            Redirect.objects.update_or_create(
                site=se_site,
                old_path=old_category_.url,
                defaults={'new_path': new_category_.url},
            )

    def update_products(product_data, new_category_):
        products = Product.objects.filter(id__in=product_data.keys())
        for product in products:
            product.uuid = product_data[str(product.id)]
            product.category = new_category_
            product.save()

    def merge(category_data_, parent=None):
        for uuid, data in category_data_.items():
            new_category = Category.objects.create(
                uuid=uuid,
                name=data['name'],
                parent=parent,
            )

            if uuid in CATEGORY_UUID_ID_MAP:
                old_category = Category.objects.get(id=CATEGORY_UUID_ID_MAP[uuid])
                merge_meta_data(old_category, new_category)
                create_redirects(old_category, new_category)

            if data['products_data']:
                update_products(data['products_data'], new_category)

            if data['children']:
                merge(data['children'], new_category)

    merge(category_data)

    Page.objects.filter(shopelectro_category__in=categories_on_delete).delete()
    Category.objects.filter(id__in=categories_on_delete).delete()

    print('Was created {} redirects...'.format(Redirect.objects.count() - old_redirects_count))


@transaction.atomic
def set_db_sequence():
    """Set the sequences to the last used id."""
    category_highest_number_in_sequence = Category.objects.all().order_by('-id').first().id + 1
    product_highest_number_in_sequence = Product.objects.all().order_by('-id').first().id + 1

    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER SEQUENCE shopelectro_category_id_seq RESTART WITH %s;'
            % category_highest_number_in_sequence,
        )

        cursor.execute(
            'ALTER SEQUENCE shopelectro_product_id_seq RESTART WITH %s;'
            % product_highest_number_in_sequence,
        )


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        start = time.time()

        set_db_sequence()

        with xml_command.download_catalog(settings.ASSETS_DIR):
            with Category.objects.disable_mptt_updates(), Page.objects.disable_mptt_updates():
                merge_catalog(merge_data(
                    category_data=xml_command.get_data(**CATEGORY_CONFIG),
                    product_data=xml_command.get_data(**PRODUCT_CONFIG),
                ))

        Category.objects.rebuild()
        Page.objects.rebuild()

        print('Merge catalog completed! {0:.1f} seconds elapsed.'.format(time.time() - start))
