from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings

from pages.models import ModelPage
from catalog.models import AbstractProduct, AbstractCategory
from pages.models import Page
from ecommerce.models import Order as ecOrder


class Category(AbstractCategory):
    """
    SE-specific Category model.

    Define product_relation class attribute to make use of
    get_recursive_products_with_count method in its abstract
    superclass.
    """
    product_relation = 'products'
    TREE_PAGE_SLUG = 'catalog'

    @property
    def image(self):
        products = self.products.all()
        return products[0].image if products else None

    def get_absolute_url(self):
        """Return url for model."""
        return reverse('category', args=(self.slug,))


class Product(AbstractProduct):
    """
    SE-specific Product model.

    Define n:1 relation with SE-Category and 1:n with Property.
    Add wholesale prices.
    """

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, default=None,
        related_name='products', db_index=True
    )

    purchase_price = models.FloatField(default=0)
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

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)


class Property(models.Model):
    """Property of a Product."""
    name = models.CharField(max_length=255, db_index=True)
    is_numeric = models.SmallIntegerField(default=0)
    value = models.CharField(max_length=255)
    product = models.ForeignKey(Product, db_index=True)

    def __str__(self):
        return self.name


def _default_payment():
    """Return default payment option, which is first element of first tuple in options."""
    assert settings.PAYMENT_OPTIONS[0][0], 'No payment options!'
    return settings.PAYMENT_OPTIONS[0][0]


class Order(ecOrder):
    """Extended Order model."""
    payment_type = models.CharField(
        max_length=255,
        choices=settings.PAYMENT_OPTIONS,
        default=_default_payment()
    )

    @property
    def payment_type_name(self):
        """Return name for an order's payment option."""
        return next(
            name for option, name in settings.PAYMENT_OPTIONS
            if self.payment_type == option
        )


def create_page_managers(*args: [models.Model]):
    """Create managers for dividing ModelPage entities"""
    def is_correct_arg(arg):
        return isinstance(arg, type(models.Model))

    assert all(map(is_correct_arg, args)), 'args should be ModelBase type'

    def create_manager(model):
        class ModelPageManager(models.Manager):
            def get_queryset(self):
                return super(ModelPageManager, self).get_queryset().filter(
                    related_model_name=model._meta.db_table)
        return ModelPageManager

    return [create_manager(model) for model in args]

CategoryPageManager, ProductPageManager = create_page_managers(Category, Product)


class CategoryPage(ModelPage):
    class Meta(ModelPage.Meta):
        proxy = True

    objects = CategoryPageManager()


class ProductPage(ModelPage):
    class Meta(ModelPage.Meta):
        proxy = True

    objects = ProductPageManager()
