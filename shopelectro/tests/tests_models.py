from itertools import chain
from functools import partial

from django.conf import settings
from django.forms.models import model_to_dict
from django.test import TestCase, TransactionTestCase

from shopelectro.models import Product, Tag, TagGroup
from shopelectro.tests.helpers import create_doubled_tag


class ProductModel(TestCase):

    fixtures = ['dump.json']

    def test_creation_deactivated_product(self):
        """Creation of a deactivated product does not fail."""
        unactive_product = Product.objects.first()
        unactive_product.page.is_active = False
        unactive_product.page.save()

        try:
            Product.objects.create(**model_to_dict(
                unactive_product,
                ['name', 'price', 'vendor_code', 'uuid'],
            ))
        except Exception as error:
            self.fail(f'Creation of existing product failed: {{ error }}')


class TagModel(TestCase):

    fixtures = ['dump.json']

    def get_products(self):
        return Product.objects.all()[:3]

    def test_get_brands_content(self):
        brand_group = TagGroup.objects.get(name=settings.BRAND_TAG_GROUP_NAME)
        for product, tag in Tag.objects.get_brands(self.get_products()).items():
            self.assertEquals(tag.group, brand_group)
            self.assertIn(product, tag.products.all())

    def test_filter_by_products(self):
        sort_by_id = partial(sorted, key=lambda x: x.id)
        products = self.get_products()
        self.assertEquals(
            sort_by_id(Tag.objects.filter_by_products(products)),
            sort_by_id(list(set(
                chain.from_iterable(product.tags.all() for product in products)
            ))),
        )

    def test_double_named_tag_saving(self):
        """Two tags with the same name should have unique slugs."""
        tag_from = Tag.objects.first()
        tag_to = create_doubled_tag(tag_from)
        self.assertNotEqual(tag_from.slug, tag_to.slug)


class QueryQuantities(TransactionTestCase):
    """Test quantity of db-queries for different methods."""

    fixtures = ['dump.json']

    def test_get_brands_from_tags(self):
        """Perform two queries to fetch tags, its products."""
        product = list(Product.objects.all())
        with self.assertNumQueries(2):
            Tag.objects.get_brands(product)

    def test_get_brands_from_products(self):
        """
        Perform a lot of queries, so we should fetch brands from the Tag model.

        @todo #525:30m Try to implement Product.objects.get_brands()
         Currently we use Tag.objects.get_brands(), be it seems is not so convenient
         as it may be.
         Details:
         https://github.com/fidals/shopelectro/pull/531#discussion_r211858857
         https://github.com/fidals/shopelectro/pull/531#discussion_r211962280
        """
        products = Product.objects.all().prefetch_related('tags', 'tags__group')
        products_quantity = products.count() + 3

        with self.assertNumQueries(products_quantity):
            {
                p: p.tags.filter(group__name=settings.BRAND_TAG_GROUP_NAME).first()
                for p in products
            }
