from typing import Optional
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

    def __str__(self):
        return self.name


class TagQuerySet(models.QuerySet):

    def filter_by_products(self, products: typing.List[Product]):
        ordering = settings.TAGS_ORDER
        distinct = [order.lstrip('-') for order in ordering]

        return (
            self
            .filter(products__in=products)
            .order_by(*ordering)
            .distinct(*distinct, 'id')
        )

    def get_group_tags_pairs(self) -> typing.List[typing.Tuple[TagGroup, typing.List['Tag']]]:
        grouped_tags = groupby(self.prefetch_related('group'), key=attrgetter('group'))
        return [
            (group, list(tags_))
            for group, tags_ in grouped_tags
        ]

    def get_brands(self, products: typing.List[Product]) -> typing.Dict[Product, 'Tag']:
        brand_tags = (
            self.filter(group__name=settings.BRAND_TAG_GROUP_NAME)
            .prefetch_related('products')
            .select_related('group')
        )

        return {
            product: brand
            for brand in brand_tags for product in products
            if product in brand.products.all()
        }

    def as_string(  # Ignore PyDocStyleBear
        self,
        field_name: str,
        type_delimiter: str,
        group_delimiter: str,
    ) -> str:
        """
        :param field_name: Only field's value is used to represent tag as string.
        :param type_delimiter:
        :param group_delimiter:
        :return:
        """
        if not self:
            return ''

        group_tags_map = self.get_group_tags_pairs()

        _, tags_by_group = zip(*group_tags_map)

        return group_delimiter.join(
            type_delimiter.join(getattr(tag, field_name) for tag in tags_list)
            for tags_list in tags_by_group
        )

    def as_title(self) -> str:
        return self.as_string(
            field_name='name',
            type_delimiter=settings.TAGS_TITLE_DELIMITER,
            group_delimiter=settings.TAG_GROUPS_TITLE_DELIMITER
        )

    def as_url(self) -> str:
        return self.as_string(
            field_name='slug',
            type_delimiter=settings.TAGS_URL_DELIMITER,
            group_delimiter=settings.TAG_GROUPS_URL_DELIMITER
        )


class TagManager(models.Manager.from_queryset(TagQuerySet)):

    def get_queryset(self):
        return (
            super().get_queryset()
            .order_by(*settings.TAGS_ORDER)
        )

    def get_group_tags_pairs(self):
        return self.get_queryset().get_group_tags_pairs()

    def filter_by_products(self, products):
        return self.get_queryset().filter_by_products(products)

    def get_brands(self, products):
        """Get a batch of products' brands."""
        return self.get_queryset().get_brands(products)


class Tag(models.Model):

    # Uncomment it after moving to refarm with rf#162
    # class Meta:
    #     unique_together = ('name', 'group')

    objects = TagManager()

    uuid = models.UUIDField(default=uuid4, editable=False)
    name = models.CharField(
        max_length=100, db_index=True, verbose_name=_('name'))
    position = models.PositiveSmallIntegerField(
        default=0, blank=True, db_index=True, verbose_name=_('position'),
    )

    # Set it as unique with rf#162
    slug = models.SlugField(default='')

    group = models.ForeignKey(
        TagGroup, on_delete=models.CASCADE, null=True, related_name='tags',
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            # same slugify code used in PageMixin object
            self.slug = slugify(
                unidecode(self.name.replace('.', '-').replace('+', '-'))
            )
        doubled_tag_qs = self.__class__.objects.filter(slug=self.slug)
        if doubled_tag_qs:
            self.slug = randomize_slug(self.slug)
        super(Tag, self).save(*args, **kwargs)

    @staticmethod
    def parse_url_tags(tags: str) -> list:
        groups = tags.split(settings.TAGS_URL_DELIMITER)
        return set(chain.from_iterable(
            group.split(settings.TAG_GROUPS_URL_DELIMITER) for group in groups
        ))


class ExcludedModelTPageManager(PageManager):

    def get_queryset(self):
        return super().get_queryset().exclude(type=Page.MODEL_TYPE)


class ExcludedModelTPage(Page):

    class Meta(Page.Meta):  # Ignore PycodestyleBear (E303)
        proxy = True

    objects = ExcludedModelTPageManager()
