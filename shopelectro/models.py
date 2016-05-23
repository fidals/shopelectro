"""
Catalog extended models: Category and Product.
"""
import os
from django.db import models
from django.conf import settings
from catalog.models import Category, Product


class ProductExtended(Product):
    """
    Product extended model.
    Extends basic functionality and primitives for Product model.
    Has n:1 relation with Category.
    """

    price_small = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    price_medium = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    price_large = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def get_images(self):
        """:return: all product images"""
        product_folder = 'images/catalog/products/' + str(self.id)
        static = os.path.join(settings.STATIC_ROOT, product_folder)

        try:
            images_array = \
                [os.path.join(product_folder, file) for file in os.listdir(static) if not file.startswith('small')]
        except FileNotFoundError:
            return []

        return list(reversed(images_array))
