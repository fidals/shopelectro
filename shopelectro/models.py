import os
from django.db import models
from django.conf import settings

from catalog import models as catalog_models


class Product(catalog_models.Product):
    wholesale_small = models.FloatField()
    wholesale_medium = models.FloatField()
    wholesale_large = models.FloatField()

    @property
    def trademark(self):
        """Return value of trademark property if exists."""
        try:
            return self.property_set.get(name='Товарный знак').value
        except Property.DoesNotExist:
            return

    def get_images(self):
        """:return: all product images"""
        product_folder = 'images/catalog/products/' + str(self.id)
        static = os.path.join(settings.STATIC_ROOT, product_folder)

        try:
            images_array = [os.path.normpath(
                                os.path.join(product_folder, file))
                            for file in os.listdir(static)
                            if not file.startswith('small')]
        except FileNotFoundError:
            return []

        return list(reversed(images_array))


class Property(models.Model):
    name = models.CharField(max_length=255)
    is_numeric = models.SmallIntegerField(default=0)
    value = models.CharField(max_length=255)
    product = models.ForeignKey(Product)

    def __str__(self):
        return self.name
