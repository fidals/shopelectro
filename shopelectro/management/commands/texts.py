"""
Don't review it. We'll kick out this code after first deploy.
Temporary command. Import texts from 1C categories and products to pages.
"""

import os
import time
import typing
from ftplib import FTP
from functools import wraps
from xml.etree import ElementTree

from django.core.management.base import BaseCommand

from shopelectro.models import Product, Category


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
            print(result or 'Completed: {}'.format(procedure_name))
        return wrapper
    return inner


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

    @process('Load info to DB')
    def handle(self, *args: tuple, **options: dict) -> str:
        """Run 'import' command."""
        start_time = time.time()
        self.get_xml_files()
        self.update_category_pages()
        self.update_product_pages()
        self.remove_xml()
        return 'Completed: {0:.1f} seconds'.format(time.time() - start_time)

    def update_category_pages(self) -> typing.Generator:
        """Parse XML and return categories's generator."""
        catalog = self.categories_in_xml

        def get_id(category):
            """Return category id."""
            return int(category.attrib['folder_id'])

        for xml_category in catalog:
            category = Category.objects.get(id=get_id(xml_category))

            xml_content = xml_category.find('description')
            if xml_content:
                category.page.content = xml_content.text.strip()

            xml_seo_text = xml_category.attrib['seotext']
            if xml_seo_text:
                category.page.seo_text = xml_seo_text.strip()

            if xml_content or xml_seo_text:
                category.page.save()

    def update_product_pages(self) -> typing.Generator:
        """Parse XML and return product's generator."""
        catalog = self.products_in_xml

        for xml_product in catalog:
            id = int(xml_product.attrib['element_id'])
            products_list = list(Product.objects.filter(id=id).iterator())
            if not products_list:
                continue
            product = products_list[0]
            xml_content = xml_product[0].text

            if xml_content:
                product.page.content = xml_content
                product.page.save()

    @process('Download xml files')
    def get_xml_files(self) -> result_message:
        """Downloads xml files from FTP."""
        def download_file():
            """Download given file using FTP connection."""
            ftp.cwd(self.FTP_XML_PATH)
            ftp.retrbinary('RETR {}'.format(xml_file), save_xml.write)

        for xml_file in self.XML_FILES:
            with FTP(**self.FTP_CONNECTION) as ftp, open(xml_file, 'wb') as save_xml:
                download_file()
        return 'XML files downloaded.'

    @process('Remove files')
    def remove_xml(self) -> result_message:
        """Remove downloaded xml files."""
        for xml in self.XML_FILES:
            os.remove(xml)
