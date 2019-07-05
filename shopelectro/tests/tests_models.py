from functools import partial
from itertools import chain

from django.conf import settings
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
from django.test import TestCase, TransactionTestCase, tag

from shopelectro.models import Category, MatrixBlock, Product, Tag, TagGroup


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

    def test_get_matrix_blocks(self):
        roots_count = Category.objects.active().filter(level=0).count()
        blocks = MatrixBlock.objects.blocks()

        # 2 queries: MatrixBlock + Category joined with CategoryPage
        # select_related doesn't deffer the queries
        with self.assertNumQueries(2):
            self.assertEquals(roots_count, len(blocks))
            for block in blocks:
                self.assertTrue(block.category)
                self.assertTrue(block.category.page)

        with self.assertNumQueries(2):
            for block in blocks:
                self.assertTrue(block.rows())


@tag('fast')
class MatrixBlockModel(TestCase):

    fixtures = ['dump.json']

    def count_all_rows(self, block: MatrixBlock) -> int:
        return block.category.children.active().count()

    def test_block_category_relation_uniqueness(self):
        block = MatrixBlock.objects.first()

        with self.assertRaises(IntegrityError):
            MatrixBlock.objects.create(category=block.category)

    def test_unsized_rows_count(self):
        block = MatrixBlock.objects.filter(block_size=None).first()

        self.assertEquals(
            self.count_all_rows(block),
            block.rows().count(),
        )

    def test_sized_rows_count(self):
        sized_block, oversized_block = MatrixBlock.objects.all()[:2]

        # block_size < category's children quantity
        sized_block.block_size = self.count_all_rows(sized_block) - 1
        sized_block.save()

        self.assertGreater(
            self.count_all_rows(sized_block),
            sized_block.rows().count(),
        )
        self.assertEquals(
            sized_block.block_size,
            sized_block.rows().count(),
        )

        # block_size > category's children quantity
        oversized_block.block_size = self.count_all_rows(oversized_block) + 1
        oversized_block.save()

        self.assertEquals(
            self.count_all_rows(oversized_block),
            oversized_block.rows().count(),
        )
        self.assertGreater(
            oversized_block.block_size,
            oversized_block.rows().count(),
        )
