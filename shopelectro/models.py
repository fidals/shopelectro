from itertools import chain, groupby
from operator import attrgetter
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode

from catalog.models import (
    AbstractProduct, AbstractCategory
)
from ecommerce.models import Order as ecOrder
from pages.models import CustomPage, ModelPage, SyncPageMixin


class Category(AbstractCategory, SyncPageMixin):

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
    """
    Define n:1 relation with SE-Category and 1:n with Property.
    Add wholesale prices.
    """

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

    @property
    def params(self):
        return Tag.objects.filter(products=self).get_group_tags_pairs()


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
    """
    Return default payment option, which is first element of
    first tuple in options.
    """
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
        """
        Save cart's state into Order instance.
        :param cart: user's cart
        :return: self
        """
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
    class Meta(ModelPage.Meta):
        proxy = True

    objects = ModelPage.create_model_page_managers(Category)


class ProductPage(ModelPage):
    """Create proxy model for Admin."""
    class Meta(ModelPage.Meta):
        proxy = True

    objects = ModelPage.create_model_page_managers(Product)


class TagGroup(models.Model):

    uuid = models.UUIDField(default=uuid4, editable=False)  # Ignore CPDBear
    name = models.CharField(
        max_length=100, db_index=True, verbose_name=_('name'))
    position = models.PositiveSmallIntegerField(
        default=0, blank=True, db_index=True, verbose_name=_('position'),
    )

    def __str__(self):
        return self.name


class TagQuerySet(models.QuerySet):

    def get_group_tags_pairs(self):
        ordering = ['group__position', 'group__name', 'position', 'name']
        distinct = [order.lstrip('-') for order in ordering]

        tags = (
            self
            .all()
            .prefetch_related('group')
            .order_by(*ordering)
            .distinct(*distinct, 'id')
        )

        group_tags_pair = [
            (group, list(tags_))
            for group, tags_ in groupby(tags, key=attrgetter('group'))
        ]

        return group_tags_pair


class TagManager(models.Manager):

    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)

    def get_group_tags_pairs(self):
        return self.get_queryset().get_group_tags_pairs()


URL_TAGS_TYPE_DELIMITER = '-or-'
URL_TAGS_GROUP_DELIMITER = '-and-'

TITLE_TAGS_TYPE_DELIMITER = ' или '
TITLE_TAGS_GROUP_DELIMITER = ' и '


class Tag(models.Model):

    objects = TagManager()

    uuid = models.UUIDField(default=uuid4, editable=False)
    name = models.CharField(
        max_length=100, db_index=True, verbose_name=_('name'))
    position = models.PositiveSmallIntegerField(
        default=0, blank=True, db_index=True, verbose_name=_('position'),
    )

    slug = models.SlugField(default='')

    group = models.ForeignKey(
        TagGroup, on_delete=models.CASCADE, null=True, related_name='tags',
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # same slugify code used in PageMixin object
            self.slug = slugify(
                unidecode(self.name.replace('.', '-').replace('+', '-'))
            )
        super(Tag, self).save(*args, **kwargs)

    @staticmethod
    def serialize_tags(
        pairs: list,
        field_name: str,
        type_delimiter: str,
        group_delimiter: str
    ) -> str:
        _, tags_by_group = zip(*pairs)
        return group_delimiter.join(
            type_delimiter.join(getattr(tag, field_name) for tag in tags)
            for tags in tags_by_group
        )

    @staticmethod
    def serialize_url_tags(tags: list) -> str:
        return Tag.serialize_tags(
            tags, 'slug', URL_TAGS_TYPE_DELIMITER, URL_TAGS_GROUP_DELIMITER
        )

    @staticmethod
    def parse_url_tags(tags: str) -> list:
        groups = tags.split(URL_TAGS_GROUP_DELIMITER)
        return set(chain.from_iterable(
            group.split(URL_TAGS_TYPE_DELIMITER) for group in groups
        ))

    @staticmethod
    def serialize_title_tags(tags: list) -> str:
        return Tag.serialize_tags(
            tags, 'name', TITLE_TAGS_TYPE_DELIMITER, TITLE_TAGS_GROUP_DELIMITER
        )
