from django.db import models
from django.conf import settings

from catalog.models import AbstractProduct
from . import images


class Product(AbstractProduct):
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


class Property(models.Model):
    name = models.CharField(max_length=255)
    is_numeric = models.SmallIntegerField(default=0)
    value = models.CharField(max_length=255)
    product = models.ForeignKey(Product)

    def __str__(self):
        return self.name
