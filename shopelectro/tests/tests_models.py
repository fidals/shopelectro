"""Defines tests for models in Shopelectro app."""

import os
from django.conf import settings
from django.test import TestCase

from catalog.models import Category
from shopelectro.models import Product, Property


class ModelsTests(TestCase):
    """Test suite for models."""

    def setUp(self):
        """
        Defines testing data.
        """
        self.category, _ = Category.objects.get_or_create(
            name='Test category'
        )

        self.product, _ = Product.objects.get_or_create(
            id=3993,
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

    def test_get_image(self):
        """
        Get product's images or return image thumbnail.
        """

        main_image_path = os.path.normpath(
            'images/catalog/products/' + str(self.product.id) + '/main.jpg')
        images_list = self.product.get_images()

        if images_list:
            self.assertIn(
                images_list[0],
                main_image_path
            )
        else:
            image_name = settings.IMAGE_THUMBNAIL
            self.assertEqual(image_name, 'images/logo.png')

    def test_get_trademark(self):
        """Trademark property of Product object should return value of respective Property object."""
        self.assertEqual(self.product.trademark, self.trademark.value)
