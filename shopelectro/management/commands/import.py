import xml.etree.ElementTree as etree
from django.core.management.base import BaseCommand
from catalog.models import Product, Category
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    """
    Import catalog command.
    """
    help = 'Import catalog from .xml file'
    ROOT_CATEGORY = 132

    def add_arguments(self, parser):
        parser.add_argument('categories', type=str)
        parser.add_argument('products', type=str)

    def handle(self, *args, **options):
        """
        Runs command
        :param args:
        :param options:
        :return:
        """
        xml_categories = etree.parse(options['categories'])
        self.proceed_categories(xml_categories.getroot().find('catalog2_1'))

        xml_products = etree.parse(options['products'])
        self.proceed_products(xml_products.getroot())

    def proceed_categories(self, catalog):
        """
        Import categories.
        Proceeds every category node which is a child of 'catalog2_1' element except from first
        which is 'ShopElectro'-root.
        :param catalog:
        :return:
        """
        self.stdout.write("Start categories import...")

        for category in catalog[1:]:
            category_object = Category(name=category.text,
                                       id=int(category.attrib['folder_id']))
            parent_id = int(category.attrib['parent_id'])
            if parent_id != self.ROOT_CATEGORY:
                category_object.parent = Category.objects.get(id=parent_id)
            category_object.save()

        self.stdout.write("Finish importing categories!")

    def proceed_products(self, catalog):
        """
        Proceeds products from a given XML's entry.
        :param catalog:
        :return:
        """
        self.stdout.write("Start products import...")

        for product in catalog:
            if product.attrib['parent_id2_1']:
                kwargs = self.get_product_kwargs(product)
                if kwargs:
                    product_object = Product(**kwargs)
                    product_object.save()

        self.stdout.write("Finish importing products!")

    @staticmethod
    def get_product_kwargs(node):
        """
        Gets product's info for given node in XML.
        If XML's data is invalid, returns None
        :param node:
        :return:
        """
        def get_stock():
            """
            Calculate stock for proceeding product.
            We don't pass it explicitly because of closure on enclosing environment.
            :return:
            """
            stock_list = [int(x) for x in [node.attrib['stock_elizar'],
                                           node.attrib['stock_yunona'],
                                           node.attrib['stock_main']]]
            sum_stock = sum(stock_list)
            return sum_stock if sum_stock > 0 else 0

        product_data = {
            'id': int(node.attrib['element_id']),
            'name': node.attrib['element_name'],
            'in_stock': get_stock(),
            'description': node[0].text if node[0].text else "",
            'price': int(node[2][0].attrib['price_cost'])
        }
        if node.attrib['parent_id2_1']:
            try:
                product_data['category'] = Category.objects.get(id=int(node.attrib['parent_id2_1']))
            except ObjectDoesNotExist:
                return
        return product_data
