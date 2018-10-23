import random
import string
import typing
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from catalog import models as catalog_models
from ecommerce import models as ecommerce_models
from pages import models as pages_models


def randomize_slug(slug: str) -> str:
    slug_hash = ''.join(
        random.choices(string.ascii_lowercase, k=settings.SLUG_HASH_SIZE)
    )
    return f'{slug}_{slug_hash}'


class SECategoryQuerySet(catalog_models.CategoryQuerySet):
    def get_categories_tree_with_pictures(self) -> 'SECategoryQuerySet':
        categories_with_pictures = (
            self
            .filter(products__page__images__isnull=False)
            .distinct()
        )

        return categories_with_pictures.get_ancestors(include_self=True)


class SECategoryManager(
    catalog_models.CategoryManager.from_queryset(SECategoryQuerySet)
):
    pass


class Category(catalog_models.AbstractCategory, pages_models.SyncPageMixin):

    objects = SECategoryManager()
    # pages.models.Page.objects_ field. It has the same problem.
    objects_ = SECategoryManager()
    uuid = models.UUIDField(default=uuid4, editable=False)

    @classmethod
    def get_default_parent(cls):
        return pages_models.CustomPage.objects.filter(slug='catalog').first()

    @property
    def image(self):
        products = self.products.all()
        return products[0].image if products else None

    def get_absolute_url(self):
        return reverse('category', args=(self.page.slug,))


class Product(catalog_models.AbstractProduct, pages_models.SyncPageMixin):

    # That's why we are needed to explicitly add objects manager here
    # because of Django special managers behaviour.
    # Se se#480 for details.
    objects = catalog_models.ProductManager()

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

    def get_brand_name(self) -> str:
        brand: typing.Optional['Tag'] = Tag.objects.get_brands([self]).get(self)
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


class Order(ecommerce_models.Order):
    address = models.TextField(blank=True, default='')
    payment_type = models.CharField(
        max_length=255,
        choices=settings.PAYMENT_OPTIONS,
        default=_default_payment()
    )
    comment = models.TextField(blank=True, default='')
    # total price - total purchase price
    revenue = models.FloatField(default=0, verbose_name=_('revenue'))

    @property
    def payment_type_name(self):
        """Return name for an order's payment option."""
        return next(
            name for option, name in settings.PAYMENT_OPTIONS
            if self.payment_type == option
        )

    def set_positions(self, cart):
        """
        Save cart's state into Order instance.

        @todo #589:60m Create Cart model.
         See details here: https://github.com/fidals/shopelectro/pull/590#discussion_r222544672
        """
        self.revenue = cart.total_revenue()
        self.save()
        for id_, position in cart:
            self.positions.create(
                order=self,
                product_id=id_,
                vendor_code=position['vendor_code'],
                name=position['name'],
                price=position['price'],
                quantity=position['quantity'],
            )
        return self


class CategoryPage(pages_models.ModelPage):
    """Create proxy model for Admin."""

    class Meta(pages_models.ModelPage.Meta):  # Ignore PycodestyleBear (E303)
        proxy = True

    # noinspection PyTypeChecker
    objects = pages_models.ModelPage.create_model_page_managers(Category)


class ProductPage(pages_models.ModelPage):
    """Create proxy model for Admin."""

    class Meta(pages_models.ModelPage.Meta):  # Ignore PycodestyleBear (E303)
        proxy = True

    # noinspection PyTypeChecker
    objects = (
        pages_models.ModelPage
        .create_model_page_managers(Product)
    )


class TagGroup(catalog_models.TagGroup):
    pass


class TagQuerySet(catalog_models.TagQuerySet):
    pass


class Tag(catalog_models.Tag):
    group = models.ForeignKey(
        TagGroup, on_delete=models.CASCADE, null=True, related_name='tags',
    )


class ExcludedModelTPageQuerySet(pages_models.PageQuerySet):
    def exclude_type(self):
        return self.exclude(type=pages_models.Page.MODEL_TYPE)

# @todo #rf169:30m Fix model.Manager bad inheritance
#  Now we have this problem:
#  ```
#  In [2]: type(ExcludedModelTPage.objects.all())
#  Out[2]: mptt.querysets.TreeQuerySet
#  ```
#  But should be `pages.models.PageQuerySet`.
#  Or just rm all excluded staff
#  in favor on direct excluded filter using.
class ExcludedModelTPageManager(
    models.Manager.from_queryset(ExcludedModelTPageQuerySet)
):

    def get_queryset(self):
        return super().get_queryset().exclude(type=pages_models.Page.MODEL_TYPE)


class ExcludedModelTPage(pages_models.Page):

    class Meta(pages_models.Page.Meta):  # Ignore PycodestyleBear (E303)
        proxy = True

    objects = ExcludedModelTPageManager()
    # pages.models.Page.objects_ field. It has the same problem.
    objects_ = ExcludedModelTPageManager()
