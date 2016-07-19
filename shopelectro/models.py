from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from catalog.models import AbstractProduct, AbstractCategory
from ecommerce.models import Order as ecOrder


class Category(AbstractCategory):
    """
    SE-specific Category model.

    Define product_relation class attribute to make use of
    get_recursive_products_with_count method in its abstract
    superclass.
    """
    product_relation = 'products'

    def get_absolute_url(self):
        """Return url for model."""
        return reverse('category', args=(self.slug,))


class Product(AbstractProduct):
    """
    SE-specific Product model.

    Define n:1 relation with SE-Category and 1:n with Property.
    Add wholesale prices.
    """
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='products')
    wholesale_small = models.FloatField()
    wholesale_medium = models.FloatField()
    wholesale_large = models.FloatField()

    def get_absolute_url(self):
        return reverse('product', args=(self.id,))

    @property
    def trademark(self):
        """Return value of trademark property if exists."""

        try:
            return self.property_set.get(name='Товарный знак').value
        except Property.DoesNotExist:
            return


class Property(models.Model):
    """Property of a Product."""
    name = models.CharField(max_length=255)
    is_numeric = models.SmallIntegerField(default=0)
    value = models.CharField(max_length=255)
    product = models.ForeignKey(Product)

    def __str__(self):
        return self.name


def _default_payment():
    """Return default payment option, which is first element of first tuple in options."""
    assert settings.PAYMENT_OPTIONS[0][0], 'No payment options!'
    return settings.PAYMENT_OPTIONS[0][0]


class Order(ecOrder):
    """Extended Order model."""
    payment_option = models.CharField(max_length=255,
                                      choices=settings.PAYMENT_OPTIONS,
                                      default=_default_payment())
