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


result_message = str  # Type alias for returning result information

CATEGORY_POSITIONS = {
    24: 1, 22: 2, 18: 3, 17: 4, 7: 5, 137: 1, 160: 2,
    157: 3, 25: 4, 155: 5, 152: 6, 26: 7, 34: 8, 35: 9, 36: 10, 27: 11, 138: 1,
    41: 2, 40: 3, 39: 4, 38: 5, 37: 6, 55: 1, 54: 2, 53: 3, 52: 4, 48: 5,
    153: 1, 151: 2, 170: 3, 167: 4, 169: 5, 150: 6, 145: 7, 81: 8, 74: 9,
    104: 10, 111: 11, 140: 12, 63: 13, 6: 1, 2: 2, 3: 3, 4: 4, 5: 5,
}

CATEGORY_TITLE = '{name} купить в интернет-магазине - ShopElectro'
CATEGORY_TITLE_WITH_PRICE = '{name} купить в интернет-магазине, цена от {price} руб - ShopElectro'

CATEGORY_SEO_TEXT_SUFFIX = '''
    Наши цены ниже, чем у конкурентов, потому что мы покупаем напрямую у производителя.
'''

PRODUCT_TITLE = '''
    {name} - купить недорого, со скидкой в интернет-магазине ShopElectro, цена - {price} руб
'''

PRODUCT_DESCRIPTION = '''
    {name} - Элементы питания, зарядные устройства, ремонт. Купить
    {category_name} в Санкт Петербурге.
'''

# passive mode of ftp connection.
# This option depends on ftp server settings
FTP_PASSIVE_MODE = True


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
def update_and_delete(model_generator_mapping: list) -> result_message:
    """Perform db transaction of updating entity or creating new ones."""
    def update_instances(Model, collection) -> list:
        """Save instances from generator into db."""
        saved_entity_ids = []
        created_entities = 0
        for entity_id, entity_data in collection:
            entity, is_created = Model.objects.update_or_create(id=entity_id, defaults=entity_data)
            update_page_data(entity)

            saved_entity_ids.append(entity.id)
            if is_created:
                created_entities += 1

        print('{1} {0} were updated...\n{2} {0} were created...'.format(
            Model._meta.verbose_name_plural,
            len(saved_entity_ids) - created_entities,
            created_entities
        ))

        return saved_entity_ids

    def delete_instances(Model, entity_ids):
        instances_for_delete = Model.objects.exclude(id__in=entity_ids)
        count = instances_for_delete.count()
        # https://goo.gl/61kj19
        for instance in instances_for_delete:
            instance.delete()
        print('{} {} were deleted'.format(
            count, Model._meta.verbose_name_plural))

    with transaction.atomic():
        for model_class, generator in model_generator_mapping:
            updated_ids = update_instances(model_class, generator)
            delete_instances(model_class, updated_ids)

    return 'Categories and Products were saved to DB.'


def update_page_data(catalog_model: typing.Union[Category, Product]):
    """Create meta tags for every product and category"""
    def get_min_price(category: Category):
        """Returns min price among given category products"""
        min_product = (
            Product.objects
                   .filter(category=catalog_model)
                   .order_by('price').first()
        )
        return int(min_product.price) if min_product else 0

    page = catalog_model.page

    if isinstance(catalog_model, Category):
        min_price = get_min_price(catalog_model)
        page.title = (
            CATEGORY_TITLE_WITH_PRICE.format(
                name=page.name, price=min_price
            ) if min_price
            else CATEGORY_TITLE.format(name=page.name)
        )
        page.position = CATEGORY_POSITIONS.get(catalog_model.id, 0)
        if CATEGORY_SEO_TEXT_SUFFIX not in page.seo_text:
            page.seo_text += CATEGORY_SEO_TEXT_SUFFIX

    if isinstance(catalog_model, Product):
        category = catalog_model.category
        page.title = PRODUCT_TITLE.format(name=page.name, price=int(catalog_model.price))
        if not page.description:
            page.description = PRODUCT_DESCRIPTION.format(
                name=page.name, category_name=category.name
            )
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
        update_and_delete([
            (Category, self.parse_categories()),
            (Product, self.parse_products()),
        ])
        self.remove_xml()
        self.generate_prices()
        return 'Import completed! {0:.1f} seconds elapsed.'.format(time.time() - start_time)

    def parse_categories(self) -> typing.Generator:
        """Parse XML and return categories's generator."""

        def categories_generator(catalog):
            """Yield Category data."""

            def category_id(node):
                """Return category id."""
                return int(node.attrib['folder_id'])

            def parent_id_or_none(node):
                """Return category's parent's id or None."""
                parent_property = int(node.attrib['parent_id'])
                valid_parent = parent_property and parent_property is not self.ROOT_CATEGORY
                return parent_property if valid_parent else None

            for category in catalog:
                category_data = {
                    'name': category.text.strip(),
                    'parent_id': parent_id_or_none(category)
                }
                yield category_id(category), category_data

        return categories_generator(self.categories_in_xml)

    def parse_products(self) -> typing.Generator:
        """Parse XML and return product's generator."""

        def products_generator(catalog):
            """Yield Product's data."""

            def has_no_category(node):
                return not node.attrib['parent_id2_1']

            for product in catalog:
                if has_no_category(product):
                    continue
                product_properties = self.get_product_properties_or_none(product)
                if product_properties:
                    yield product_properties.pop('id'), product_properties

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
            ('excel',),
            ('price',),
            # to actualize generated files rendering
            ('collectstatic', '--noinput')
        ]

        for command in commands:
            call_command(*command)

        return 'Price lists were created.'
