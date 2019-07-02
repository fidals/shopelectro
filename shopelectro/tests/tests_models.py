from functools import partial
from itertools import chain

from django.conf import settings
from django.forms.models import model_to_dict
from django.test import TestCase, TransactionTestCase, tag

from shopelectro.models import Category, CatalogBlock, Product, Tag, TagGroup


@tag('fast')
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

    # @todo #589:30m Create test for Order.set_positions


@tag('fast')
class TagModel(TestCase):

    fixtures = ['dump.json']

    def get_products(self):
        return Product.objects.all()[:3]

    def test_get_brands_content(self):
        brand_group = TagGroup.objects.get(name=settings.BRAND_TAG_GROUP_NAME)
        for product, tag_ in Tag.objects.get_brands(self.get_products()).items():
            self.assertEquals(tag_.group, brand_group)
            self.assertIn(product, tag_.products.all())

    def test_filter_by_products(self):
        sort_by_id = partial(sorted, key=lambda x: x.id)
        products = self.get_products()
        self.assertEquals(
            sort_by_id(Tag.objects.filter_by_products(products)),
            sort_by_id(list(set(
                chain.from_iterable(product.tags.all() for product in products)
            ))),
        )


@tag('fast')
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

    def test_get_catalog_blocks(self):
        """Perform four queries to fetch in batch blocks, categories, pages and category's children."""
        roots = Category.objects.filter(level=0)
        roots_count = roots.count()
        for category in roots:
            CatalogBlock.objects.create(category=category)

        with self.assertNumQueries(4):
            blocks = list(CatalogBlock.objects.blocks())
            self.assertEquals(roots_count, len(blocks))
            for block in blocks:
                self.assertTrue(block.category)
                self.assertTrue(block.category.page)
                self.assertTrue(block.rows())


@tag('fast')
class CatalogBlockModel(TestCase):

    fixtures = ['dump.json']

    def test_rows_count(self):
        first, second, *_  = Category.objects.all()
        block = CatalogBlock.objects.create(category=first)
        sized_block = CatalogBlock.objects.create(category=second, block_size=2)

        self.assertNotEquals(first.children.active(), len(sized_block.rows()))
        self.assertEquals(sized_block.block_size, len(sized_block.rows()))
