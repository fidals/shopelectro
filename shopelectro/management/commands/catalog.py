"""Import catalog management command."""

from ftplib import FTP
from functools import wraps
import os
import time
import typing
from xml.etree import ElementTree

from django.db import transaction
from django.core.management import call_command
from django.core.management.base import BaseCommand

from shopelectro.models import Product, Category
from pages.models import Page


result_message = str  # Type alias for returning result information


CATEGORY_POSITIONS = {
    24: 1,
    22: 2,
    18: 3,
    17: 4,
    7: 5,
    137: 1,
    160: 2,
    157: 3,
    25: 4,
    155: 5,
    152: 6,
    26: 7,
    34: 8,
    35: 9,
    36: 10,
    27: 11,
    138: 1,
    41: 2,
    40: 3,
    39: 4,
    38: 5,
    37: 6,
    55: 1,
    54: 2,
    53: 3,
    52: 4,
    48: 5,
    153: 1,
    151: 2,
    170: 3,
    167: 4,
    169: 5,
    150: 6,
    145: 7,
    81: 8,
    74: 9,
    104: 10,
    111: 11,
    140: 12,
    63: 13,
    6: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5
}

CATEGORY_TITLE = '{h1} купить в интернет магазине shopelectro.ru в Санкт-Петербурге'
PRODUCT_TITLE = '{h1} - цены, характеристики, отзывы, описание, фотографии. Купить по выгодной ' \
                'цене в интернет-магазине shopelectro.ru Санкт-Петербург'
PRODUCT_DESCRIPTION = '{h1} - Элементы питания, зарядные устройства, ремонт. Купить ' \
                      '{category_name} в Санкт Петербурге.'

# passive mode of ftp connection.
# This option depends on ftp server settings
FTP_PASSIVE_MODE = False


def process(procedure_name: str) -> callable:
    """Print information before starting procedure and after it's been finished."""
    def inner(procedure: callable) -> callable:
        """Decorator's factory."""
        @wraps(procedure)
        def wrapper(*args: tuple, **kwargs: dict) -> None:
            """Print result before function call and after it."""
            print('{}...'.format(procedure_name))
            result = procedure(*args, **kwargs)
            print(result or 'Completed: {}'.format(procedure_name))
        return wrapper
    return inner


@process('Load info to DB')
def delete_and_create(model_generator_mapping: list) -> result_message:
    """Perform db transaction of removing current rows and creating new ones."""
    def purge_table(model):
        """Removes every row from Model's table."""
        model.objects.all().delete()

    def save_instances(collection):
        """Save instances from generator into db."""
        for instance in collection:
            instance.save()
            create_meta_tags(instance)

    with transaction.atomic():
        for model_class, generator in model_generator_mapping:
            purge_table(model_class)
            save_instances(generator)
    return 'Categories and Products were saved to DB.'


def create_meta_tags(instance):
    """Create meta tags for every product and category"""
    page = Page.objects.get(id=instance.page.id)
    h1 = page.h1

    if isinstance(instance, Category):
        if not page._title:
            page._title = CATEGORY_TITLE.format(h1=h1)
    else:
        category_name = instance.category.name
        if not page._title:
            page._title = PRODUCT_TITLE.format(h1=h1)
        if not page.description:
            page.description = PRODUCT_DESCRIPTION.format(h1=h1, category_name=category_name)

    page.save()


class Command(BaseCommand):
    """
    Import catalog command class.

    Defines configuration and methods for performing import procedure.

    Every method, which is a standalone 'process' (like getting files from FTP)
    has a @process decorator.
    Such methods should return string with information about performed task.
    """
    FTP_CONNECTION = {'host': 'office.shopelectro.ru',
                      'user': 'it_guest',
                      'passwd': '4be13e1124'}
    FTP_XML_PATH = '/shopelectro/1c/'
    XML_FILES = ['categories.xml', 'products.xml']
    XML_CATALOG_NODE = 'catalog2_1'
    ROOT_CATEGORY = 132

    @property
    def categories_in_xml(self):
        """Return a list of categories nodes presented in xml."""
        xml = ElementTree.parse(self.XML_FILES[0])
        return xml.getroot().find(self.XML_CATALOG_NODE)[1:]

    @property
    def products_in_xml(self):
        """Return a list of products nodes presented in xml."""
        return ElementTree.parse(self.XML_FILES[1]).getroot()

    @process('Import catalog')
    def handle(self, *args: tuple, **options: dict) -> str:
        """Run 'import' command."""
        start_time = time.time()
        self.get_xml_files()
        delete_and_create([
            (Category, self.parse_categories()),
            (Product, self.parse_products()),
        ])
        self.remove_xml()
        self.generate_prices()
        return 'Import completed! {0:.1f} seconds elapsed.'.format(time.time() - start_time)

    def parse_categories(self) -> typing.Generator:
        """Parse XML and return categories's generator."""
        def categories_generator(catalog):
            """Yield Category instances."""
            def category_id(node):
                """Return category id."""
                return int(node.attrib['folder_id'])

            def parent_id_or_none(node):
                """Return category's parent's id or None."""
                parent_property = int(node.attrib['parent_id'])
                valid_parent = parent_property and parent_property is not self.ROOT_CATEGORY
                return parent_property if valid_parent else None

            for category in catalog:
                yield Category(id=category_id(category),
                               name=category.text.strip(),
                               position=CATEGORY_POSITIONS.get(
                                   category_id(category), 10000),
                               parent_id=parent_id_or_none(category))
        return categories_generator(self.categories_in_xml)

    def parse_products(self) -> typing.Generator:
        """Parse XML and return product's generator."""
        def products_generator(catalog):
            """Create Product's instance and yield it."""
            def has_no_category(node):
                return not node.attrib['parent_id2_1']

            for product in catalog:
                if has_no_category(product):
                    continue
                product_properties = self.get_product_properties_or_none(
                    product)
                if product_properties:
                    yield Product(**product_properties)
        return products_generator(self.products_in_xml)

    @staticmethod
    def get_product_properties_or_none(node) -> typing.Optional[dict]:
        """Get product's info for given node in XML."""
        def stock_or_zero():
            """Return product's stock or zero if it's negative."""
            stock = sum([int(node.attrib[stock])
                         for stock in
                         ['stock_elizar', 'stock_yunona', 'stock_main']])
            return stock if stock > 0 else 0

        def category_id():
            """Get int category id."""
            return int(node.attrib['parent_id2_1'])

        assertions_data = {
            'id': int(node.attrib['element_id']),
            'price': float(node[2][0].attrib['price_cost']),
        }

        try:
            assertions_data['category'] = Category.objects.get(id=category_id())
            assert assertions_data['price']
        except Category.DoesNotExist:
            print('Category {} does not exist. Product {} will not be saved'
                  .format(category_id(), assertions_data['id']))
            return
        except AssertionError:
            print('Product with id={} have no price. It\'ll not be saved'
                  .format(assertions_data['id']))
            return

        product_data = {
            **assertions_data,
            'name': node.attrib['element_name'].strip(),
            'in_stock': stock_or_zero(),
            'wholesale_small': float(node[2][1].attrib['price_cost']),
            'wholesale_medium': float(node[2][2].attrib['price_cost']),
            'wholesale_large': float(node[2][3].attrib['price_cost']),
            'purchase_price': float(node[2][4].attrib['price_cost']),
        }

        return product_data

    @process('Download xml files')
    def get_xml_files(self) -> result_message:
        """Downloads xml files from FTP."""
        def prepare_connection():
            ftp.set_pasv(FTP_PASSIVE_MODE)  # Set passive mode off

        def download_file():
            """Download given file using FTP connection."""
            ftp.cwd(self.FTP_XML_PATH)
            ftp.retrbinary('RETR {}'.format(xml_file), save_xml.write)

        for xml_file in self.XML_FILES:
            with FTP(**self.FTP_CONNECTION) as ftp, open(xml_file, 'wb') as save_xml:
                prepare_connection()
                download_file()
        return 'XML files were downloaded.'

    @process('Remove files')
    def remove_xml(self) -> result_message:
        """Remove downloaded xml files."""
        for xml in self.XML_FILES:
            os.remove(xml)

    @staticmethod
    @process('Create price lists')
    def generate_prices() -> result_message:
        """Generate Excel, YM and Price.ru price files."""
        commands = [
            'excel',
            'price',
            # to actualize generated files rendering
            ('collectstatic', '--noinput')
        ]

        for command in commands:
            with_params = isinstance(command, tuple)
            if with_params:
                call_command(*command)
            else:
                call_command(command)

        return 'Price lists were created.'
