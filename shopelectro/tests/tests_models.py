"""Defines tests for models in Shopelectro app."""

import os
from django.conf import settings
from django.test import TestCase
from catalog.models import Category, Product


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

        product_folder_with_image = 'images/catalog/products/' + str(self.product.id)
        static = os.path.join(settings.STATIC_ROOT, product_folder_with_image)

        try:
            images_array = \
                [os.path.join(product_folder_with_image, file) for file in os.listdir(static) if not file.startswith(
                    'small')]
            reversed_list = list(reversed(images_array))

            self.assertIn(
                reversed_list[0],
                os.path.join(product_folder_with_image, 'main.jpg')
            )
        except FileNotFoundError:
            image_name = settings.IMAGE_THUMBNAIL
            self.assertEqual(image_name, 'images/logo.png')
