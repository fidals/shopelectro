from functools import reduce
from itertools import groupby, chain
from operator import attrgetter, and_

from django.db import models
from django.db.models import Avg, Q
from django.core.urlresolvers import reverse
from django.conf import settings

from catalog.models import (
    AbstractProduct, AbstractCategory, ProductManager, ProductQuerySet
)
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


class SEProductQuerySet(ProductQuerySet):

    def get_pages(self):
        """Get pages related to products."""
        return [product.page for product in self.select_related('page')]

    def get_tags(self):
        """Get unique tags related to products."""
        return set(chain.from_iterable(
            product.tags.all() for product in self.prefetch_related('tags')
        ))

    def get_by_tags(self, tags: [models.Model or int]) -> models.QuerySet:
        query = reduce(and_, (Q(tags=tag) for tag in tags))
        return self.filter(query)


class SEProductManager(ProductManager):

    def get_queryset(self):
        return SEProductQuerySet(self.model, using=self._db)

    def get_tags(self):
        return self.get_queryset().get_tags()

    def get_pages(self):
        return self.get_queryset().get_pages()

    def get_by_tags(self, tags: [models.Model]) -> models.QuerySet:
        return self.get_queryset().get_by_tags(tags)


class Product(AbstractProduct, SyncPageMixin):
    """
    Define n:1 relation with SE-Category and 1:n with Property.
    Add wholesale prices.
    """

    objects = SEProductManager()

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, related_name='products',
    )

    tags = models.ManyToManyField(
        'Tag', related_name='products',
    )

    purchase_price = models.FloatField(default=0)
    wholesale_small = models.FloatField()
    wholesale_medium = models.FloatField()
    wholesale_large = models.FloatField()

    def get_absolute_url(self):
        return reverse('product', args=(self.id,))

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


class TagGroup(models.Model):

    name = models.CharField(max_length=100, db_index=True)
    position = models.PositiveSmallIntegerField(default=0, blank=True, db_index=True)

    def __str__(self):
        return self.name


class TagQuerySet(models.QuerySet):

    def get_group_tags_pairs(self, tags=None):
        if tags:
            unique_tags = set(tags)
        else:
            unique_tags = self.all().select_related('group')

        group_tags_pair = (
            (group, list(sorted(tags_, key=attrgetter('position'))))
            for group, tags_ in groupby(unique_tags, key=attrgetter('group'))
        )

        return sorted(group_tags_pair, key=lambda x: x[0].position)


class TagManager(models.Manager):

    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)

    def get_group_tags_pairs(self, tags=None):
        return self.get_queryset().get_group_tags_pairs(tags)


class Tag(models.Model):

    name = models.CharField(max_length=100, db_index=True)
    position = models.PositiveSmallIntegerField(default=0, blank=True, db_index=True)

    objects = TagManager()

    group = models.ForeignKey(
        TagGroup, on_delete=models.CASCADE, null=True, related_name='tags',
    )

    def __str__(self):
        return self.name
