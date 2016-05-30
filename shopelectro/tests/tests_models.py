"""Defines tests for models in Shopelectro app."""

import os
from django.conf import settings
from django.test import TestCase
from catalog.models import Category
from shopelectro.models import Product


class ModelsTests(TestCase):
    """Test suite for models."""

    def setUp(self):
        """
        Defines testing data.
        """
        self.category = Category.objects.get_or_create(
            name='Test category'
        )[0]

        self.product = Product.objects.get_or_create(
            id=3993,
            category=self.category,
        )[0]

    def test_get_image(self):
        """
        Get product's images or return image thumbnail.
        """

        main_image_path = 'images/catalog/products/' + str(self.product.id) + '/main.jpg'
        images_list = self.product.get_images()

        if images_list:
            self.assertIn(
                images_list[0],
                main_image_path
            )
        else:
            image_name = settings.IMAGE_THUMBNAIL
            self.assertEqual(image_name, 'images/logo.png')
