"""Management command for generating Excel price-list."""

import os
import datetime
import openpyxl

from django.core.management.base import BaseCommand
from django.conf import settings

from catalog.models import Category
from shopelectro.models import Product


class Command(BaseCommand):
    """Command class."""
    TEMPLATE = 'template.xlsx'
    NAME = 'pricelist.xlsx'
    SHEET_TITLE = 'Прайс-лист Shopelectro'
    CATEGORY_FILL = openpyxl.styles.PatternFill(start_color='99D699',
                                                end_color='99D699',
                                                fill_type='solid')
    BUY_FILL = openpyxl.styles.PatternFill(start_color='FFCC66',
                                           end_color='FFCC66',
                                           fill_type='solid')
    CURRENT_ROW = '9'  # Start of catalog section in file.

    def handle(self, *args, **options):
        """Open template's file and start proceeding it."""
        file, sheet = self.load_file_and_sheet()
        self.fill_header(sheet)
        self.write_catalog(sheet)
        self.hide_formulas(sheet)
        file.save(self.NAME)

    def load_file_and_sheet(self):
        """
        Load template file into openpyxl.

        Return tuple with opened openpyxl file's object
        and active price sheet.
        """
        file = openpyxl.load_workbook(os.path.join(
            settings.STATIC_ROOT, self.TEMPLATE))
        return file, file.get_sheet_by_name('Прайслист')

    def fill_header(self, sheet):
        """Fill header of a sheet with date and title."""
        date_cell = 'C5'
        sheet.title = self.SHEET_TITLE
        sheet[date_cell] = datetime.date.strftime(
            datetime.date.today(), '%d.%m.%Y')

    @staticmethod
    def hide_formulas(sheet):
        """Hide formulas for calculating totals."""
        sheet.column_dimensions.group('H', 'K', hidden=True)

    def write_catalog(self, sheet):
        """Writes categories and products to sheet."""
        categories = Category.objects.all().order_by('name')
        for category in categories:
            self.write_category_with_products(sheet, category)

    def write_category_with_products(self, sheet, category):
        """Write category line and beside that - all of products in this category."""
        def write_product():
            """Write product line."""
            product_start = 'A' + self.CURRENT_ROW
            sheet[product_start] = product.name
            prices = [product.price,
                      product.wholesale_small,
                      product.wholesale_medium,
                      product.wholesale_large]
            for price, total in zip('CDEF', 'HIJK'):
                sheet[price + self.CURRENT_ROW] = prices.pop(0)
                sheet[total + self.CURRENT_ROW] = ('={0}{1}*G{1}'
                                                   .format(price, self.CURRENT_ROW))
            sheet['G' + self.CURRENT_ROW].fill = self.BUY_FILL

        def write_category_line():
            """Merge category line into one cell and write to it."""
            category_start = 'A' + self.CURRENT_ROW
            category_line = '{}:{}'.format(
                category_start, 'G' + self.CURRENT_ROW)
            sheet.merge_cells(category_line)
            sheet[category_start] = category.name
            sheet[category_start].fill = self.CATEGORY_FILL

        write_category_line()
        products = Product.objects.filter(category=category)
        for product in products:
            self.CURRENT_ROW = str(int(self.CURRENT_ROW) + 1)
            write_product()
