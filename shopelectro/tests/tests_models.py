from django.test import TestCase

from shopelectro.models import Product, Tag


class ProductModel(TestCase):

    fixtures = ['dump.json']

    def setUp(self):
        self.products = Product.objects.all()

    def test_get_products_by_tags(self):
        """Get products, that related with all given tags."""
        first_tag, second_tag = Tag.objects.first(), Tag.objects.last()
        products = Product.objects.get_by_tags([first_tag.id, second_tag.id])
        test_products = first_tag.products.all() | second_tag.products.all()

        self.assertEqual(products.count(), len(test_products))
        self.assertTrue(all(map(lambda x: x in products, test_products)))
