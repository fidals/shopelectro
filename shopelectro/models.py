import random
import string
from itertools import chain, groupby
from operator import attrgetter
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from mptt.querysets import TreeQuerySet

from catalog.models import (
    AbstractCategory,
    AbstractProduct,
    CategoryManager,
    ProductActiveManager,
    ProductManager,
    Tag as caTag,
    TagGroup as caTagGroup,
)
from ecommerce.models import Order as ecOrder
from pages.models import CustomPage, ModelPage, Page, SyncPageMixin, PageManager


class SECategoryQuerySet(TreeQuerySet):
    def get_categories_tree_with_pictures(self) -> 'SECategoryQuerySet':
        categories_with_pictures = (
            self
            .filter(products__page__images__isnull=False)
            .distinct()
        )

        return categories_with_pictures.get_ancestors(include_self=True)


class SECategoryManager(CategoryManager.from_queryset(SECategoryQuerySet)):
    pass


class Category(AbstractCategory, SyncPageMixin):

    objects = SECategoryManager()
    uuid = models.UUIDField(default=uuid4, editable=False)

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

    # That's why we are needed to explicitly add objects manager here
    # because of Django special managers behaviour.
    # Se se#480 for details.
    objects = ProductManager()
    actives = ProductActiveManager()

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        related_name='products',
        verbose_name=_('category'),
    )

    tags = models.ManyToManyField(
        'Tag',
        related_name='products',
        blank=True,
        verbose_name=_('tags'),
    )

    vendor_code = models.SmallIntegerField(verbose_name=_('vendor_code'))
    uuid = models.UUIDField(default=uuid4, editable=False)
    purchase_price = models.FloatField(
        default=0, verbose_name=_('purchase_price'))
    wholesale_small = models.FloatField(
        default=0, verbose_name=_('wholesale_small'))
    wholesale_medium = models.FloatField(
        default=0, verbose_name=_('wholesale_medium'))
    wholesale_large = models.FloatField(
        default=0, verbose_name=_('wholesale_large'))

    def get_absolute_url(self):
        return reverse('product', args=(self.vendor_code,))

    @property
    def average_rate(self):
        """Return rounded to first decimal averaged rating."""
        rating = self.product_feedbacks.aggregate(
            avg=models.Avg('rating')).get('avg', 0)
        return round(rating, 1)

    @property
    def feedback_count(self):
        return self.product_feedbacks.count()

    @property
    def feedback(self):
        return self.product_feedbacks.all().order_by('-date')

    def get_params(self):
        return Tag.objects.filter_by_products([self]).get_group_tags_pairs()

    # @todo #388:30m Move Product.get_siblings method to refarm-site
    #  And reuse it on STB.
    def get_siblings(self, offset):
        return (
            self.__class__.actives
            .filter(category=self.category)
            .prefetch_related('category')
            .select_related('page')[:offset]
        )

    def get_brand_name(self) -> str:
        brand: Optional['Tag'] = Tag.objects.get_brands([self]).get(self)
        return brand.name if brand else ''


class ProductFeedback(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True,
        related_name='product_feedbacks'
    )

    date = models.DateTimeField(
        auto_now=True, db_index=True, verbose_name=_('date'))
    name = models.CharField(
        max_length=255, db_index=True, verbose_name=_('name'))
    rating = models.PositiveSmallIntegerField(
        default=1, db_index=True, verbose_name=_('rating'))
    dignities = models.TextField(
        default='', blank=True, verbose_name=_('dignities'))
    limitations = models.TextField(
        default='', blank=True, verbose_name=_('limitations'))
    general = models.TextField(
        default='', blank=True, verbose_name=_('limitations'))


def _default_payment():
    """Default payment option is first element of first tuple in options."""
    assert settings.PAYMENT_OPTIONS[0][0], 'No payment options!'
    return settings.PAYMENT_OPTIONS[0][0]


class Order(ecOrder):
    address = models.TextField(blank=True, default='')
    payment_type = models.CharField(
        max_length=255,
        choices=settings.PAYMENT_OPTIONS,
        default=_default_payment()
    )
    comment = models.TextField(blank=True, default='')

    @property
    def payment_type_name(self):
        """Return name for an order's payment option."""
        return next(
            name for option, name in settings.PAYMENT_OPTIONS
            if self.payment_type == option
        )

    def set_positions(self, cart):
        """Save cart's state into Order instance."""
        self.save()
        for id_, position in cart:
            self.positions.create(
                order=self,
                product_id=id_,
                vendor_code=position['vendor_code'],
                name=position['name'],
                price=position['price'],
                quantity=position['quantity']
            )
        return self


class CategoryPage(ModelPage):
    """Create proxy model for Admin."""

    class Meta(ModelPage.Meta):  # Ignore PycodestyleBear (E303)
        proxy = True

    objects = ModelPage.create_model_page_managers(Category)


class ProductPage(ModelPage):
    """Create proxy model for Admin."""

    class Meta(ModelPage.Meta):  # Ignore PycodestyleBear (E303)
        proxy = True

    objects = ModelPage.create_model_page_managers(Product)


class TagGroup(caTagGroup):
    pass


class Tag(caTag):
    group = models.ForeignKey(
        TagGroup, on_delete=models.CASCADE, null=True, related_name='tags',
    )


class ExcludedModelTPageManager(PageManager):

    def get_queryset(self):
        return super().get_queryset().exclude(type=Page.MODEL_TYPE)


class ExcludedModelTPage(Page):

    class Meta(Page.Meta):  # Ignore PycodestyleBear (E303)
        proxy = True

    objects = ExcludedModelTPageManager()
