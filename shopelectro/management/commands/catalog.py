"""Import catalog management command."""

import os
import time
import typing
from ftplib import FTP
from functools import wraps
from xml.etree import ElementTree

from django.db import transaction
from django.core.management import call_command
from django.core.management.base import BaseCommand

from catalog.models import Category
from shopelectro.models import Product


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


def process(procedure_name: str) -> callable:
    """Print information before starting procedure and after it's been finished."""
    def inner(procedure: callable) -> callable:
        """Decorator's factory."""
        @wraps(procedure)
        def wrapper(*args: tuple, **kwargs: dict) -> None:
            """Print result before function call and after it."""
            print('{}...'.format(procedure_name))
            result = procedure(*args, **kwargs)
            print(result or 'Завершено: {}'.format(procedure_name))
        return wrapper
    return inner


@process('Загрузка информации в базу')
def delete_and_create(model_generator_mapping: list) -> result_message:
    """Perform db transaction of removing current rows and creating new ones."""
    def purge_table(model):
        """Removes every row from Model's table."""
        model.objects.all().delete()

    def save_instances(collection):
        """Save instances from generator into db."""
        for instance in collection:
            instance.save()

    with transaction.atomic():
        for model_class, generator in model_generator_mapping:
            # TODO: Should we pass parameters to local funcs?
            purge_table(model_class)
            save_instances(generator)
    return 'Товары и Категории успешно сохранены.'


class Command(BaseCommand):
    """
    Import catalog command class.

    Defines configuration and methods for performing import procedure.

    Every method, which is a standalone 'process' (like getting files from FTP)
    has a @process decorator.
    Such methods should return string with information about performed task.
    """
    FTP_CONNECTION = {'host': 'office.fidals.ru',
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

    @process('Импорт каталога')
    def handle(self, *args: tuple, **options: dict) -> str:
        """Run 'import' command."""
        start_time = time.time()
        self.get_xml_files()
        delete_and_create([(Category, self.parse_categories()), (Product, self.parse_products())])
        self.remove_xml()
        self.generate_prices()
        return 'Импорт завершен! Затрачено {0:.1f} секунд'.format(time.time() - start_time)

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
                               position=CATEGORY_POSITIONS.get(category_id(category), 0),
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
                product_properties = self.get_product_properties_or_none(product)
                if product_properties:
                    yield Product(**product_properties)
        return products_generator(self.products_in_xml)

    # TODO: This method could be moved into parse_products. Should we define more local funcs?
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

        product_data = {
            'id': int(node.attrib['element_id']),
            'name': node.attrib['element_name'].strip(),
            'in_stock': stock_or_zero(),
            'content': node[0].text if node[0].text else '',
            'price': float(node[2][0].attrib['price_cost']),
            'wholesale_small': float(node[2][1].attrib['price_cost']),
            'wholesale_medium': float(node[2][2].attrib['price_cost']),
            'wholesale_large': float(node[2][3].attrib['price_cost'])
        }
        try:
            product_data['category'] = Category.objects.get(id=category_id())
        except Category.DoesNotExist:
            print('Внимание! Категории {} не существует, '
                  'поэтому товар {} не будет сохранен.'
                  .format(category_id(), product_data['id']))
            return
        return product_data

    @process('Загрузка файлов')
    def get_xml_files(self) -> result_message:
        """Downloads xml files from FTP."""
        def download_file():
            """Download given file using FTP connection."""
            ftp.cwd(self.FTP_XML_PATH)
            ftp.retrbinary('RETR {}'.format(xml_file), save_xml.write)

        for xml_file in self.XML_FILES:
            with FTP(**self.FTP_CONNECTION) as ftp, open(xml_file, 'wb') as save_xml:
                download_file()
        return 'XML файлы загружены.'

    @process('Удаление файлов')
    def remove_xml(self) -> result_message:
        """Remove downloaded xml files."""
        for xml in self.XML_FILES:
            os.remove(xml)

    @staticmethod
    @process('Создание прайсов')
    def generate_prices() -> result_message:
        """Generate Excel, YM and Price.ru price files."""
        commands = ['excel', 'price']

        for command in commands:
            call_command(command)

        return 'Прайс-листы созданы.'
