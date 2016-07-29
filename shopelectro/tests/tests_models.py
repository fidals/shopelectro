"""Defines tests for models in Shopelectro app."""

import os

from django.conf import settings
from django.test import TestCase

from shopelectro.models import Product, Category, Property
from .. import images


class ModelsTests(TestCase):
    """Test suite for models."""

    def setUp(self):
        """Define testing data."""

        self.category, _ = Category.objects.get_or_create(
            name='Test category'
        )

        self.product, _ = Product.objects.get_or_create(
            id=1,
            name='Common product',
            wholesale_small=10,
            wholesale_medium=10,
            wholesale_large=10,
            category=self.category,
        )

        self.non_existing_product, _ = Product.objects.get_or_create(
            id=9999,
            name='Non existing product',
            wholesale_small=10,
            wholesale_medium=10,
            wholesale_large=10,
            category=self.category,
        )

        self.trademark, _ = Property.objects.get_or_create(
            name='Товарный знак',
            is_numeric=False,
            value='TM',
            product=self.product
        )

        self.main_image = os.path.normpath(
            'products/{}/main.jpg'.format(self.product.id))

    def test_product_images(self):
        """Get Product images."""

        images_list = images.get_images_without_small(self.product)
        self.assertIn(self.main_image, images_list)

    def test_thumbnail_image(self):
        """Get Product image thumbnail."""

        images_list = images.get_image(self.non_existing_product)
        self.assertTrue(settings.IMAGES['thumbnail'] in images_list)

    def test_main_image(self):
        """Main image property should return image."""

        self.assertTrue(images.get_image(self.product), self.main_image)

    def test_get_trademark(self):
        """
        Trademark property of Product object should return
        value of respective Property object.
        """

        self.assertEqual(self.product.trademark, self.trademark.value)
