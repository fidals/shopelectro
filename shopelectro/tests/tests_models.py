"""Defines tests for models in Shopelectro app."""

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

        self.product = Product.objects.create(
            id=99999,
            category=self.category,
            wholesale_small=10,
            wholesale_medium=10,
            wholesale_large=10,
        )

        self.trademark, _ = Property.objects.get_or_create(
            name='Товарный знак',
            product=self.product,
            defaults={
                'is_numeric': False,
                'value': 'TM',
            }
        )

        self.main_image = ('images/catalog/products/' +
                           str(self.product.id) + '/main.jpg')

    def test_get_image(self):
        """
        Get product's images or return image thumbnail.
        """
        images_list = self.product.images

        if images_list:
            self.assertIn(self.main_image, images_list)
        else:
            image_name = settings.IMAGE_THUMBNAIL
            self.assertEqual(image_name, settings.IMAGE_THUMBNAIL)

    def test_get_trademark(self):
        """
        Trademark property of Product object should return
        value of respective Property object
        """
        self.assertEqual(self.product.trademark, self.trademark.value)

    def test_main_image(self):
        """Main image property should return image, or thumbnail."""
        self.assertIn(self.product.main_image,
                      [self.main_image, settings.IMAGE_THUMBNAIL])
