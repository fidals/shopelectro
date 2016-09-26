"""Defines tests for models in Shopelectro app."""

import os

from django.test import TestCase

from shopelectro.models import Product, Category, Property


class ModelsTests(TestCase):
    """Test suite for models."""

    def setUp(self):
        self.category, _ = Category.objects.get_or_create(
            name='Test category'
        )

        self.product, _ = Product.objects.get_or_create(
            id=1,
            name='Common product',
            wholesale_small=10,
            wholesale_medium=10,
            wholesale_large=10,
            category=self.category
        )

        self.trademark, _ = Property.objects.get_or_create(
            name='Товарный знак',
            is_numeric=False,
            value='TM',
            product=self.product
        )

        self.main_image = os.path.normpath(
            'products/{}/main.jpg'.format(self.product.id))

    def test_get_trademark(self):
        """
        Trademark property of Product object should return
        value of respective Property object.
        """

        self.assertEqual(self.product.trademark, self.trademark.value)
