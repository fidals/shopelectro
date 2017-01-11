from django.db import models
from django.db.models import Avg
from django.core.urlresolvers import reverse
from django.conf import settings

from catalog.models import AbstractProduct, AbstractCategory
from ecommerce.models import Order as ecOrder
from pages.models import ModelPage, SyncPageMixin, CustomPage


class Category(AbstractCategory, SyncPageMixin):
    @classmethod
    def get_default_parent(cls):
        return CustomPage.objects.filter(slug='catalog').first()

    @property
    def image(self):
        products = self.products.all()
        return products[0].image if products else None

    def get_absolute_url(self):
        return reverse('category', args=(self.page.slug,))


class Product(AbstractProduct, SyncPageMixin):
    """
    Define n:1 relation with SE-Category and 1:n with Property.
    Add wholesale prices.
    """
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True,
        related_name='products'
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

    @property
    def average_rate(self):
        """Return rounded to first decimal averaged rating."""
        rating = self.product_feedbacks.aggregate(avg=Avg('rating')).get('avg', 0)
        return round(rating, 1)

    @property
    def feedbacks_count(self):
        return self.product_feedbacks.count()


class ProductFeedback(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True,
        related_name='product_feedbacks'
    )

    date = models.DateTimeField(auto_now=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    rating = models.PositiveSmallIntegerField(default=1, db_index=True)
    dignities = models.TextField(default='', blank=True)
    limitations = models.TextField(default='', blank=True)
    general = models.TextField(default='', blank=True)


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
    address = models.TextField(blank=True, default='')
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


class CategoryPage(ModelPage):
    """Create proxy model for Admin."""
    class Meta(ModelPage.Meta):
        proxy = True

    objects = ModelPage.create_model_page_managers(Category)


class ProductPage(ModelPage):
    """Create proxy model for Admin."""
    class Meta(ModelPage.Meta):
        proxy = True

    objects = ModelPage.create_model_page_managers(Product)
