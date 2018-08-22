from django.forms.models import model_to_dict
from django.test import TestCase

from shopelectro.models import Product, Tag, TagGroup


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


class TagTest(TestCase):

    fixtures = ['dump.json']

    def test_double_named_tag_saving(self):
        """Two tags with the same name should have unique slugs."""
        def save_doubled_tag(tag_from_):
            group_to = TagGroup.objects.exclude(id=tag_from_.group.id).first()
            tag_to = Tag(
                group=group_to, name=tag_from_.name, position=tag_from_.position
            )
            # required to create `tag.products` field
            tag_to.save()
            tag_to.products.set(tag_from.products.all())
            tag_to.save()
            return tag_to
        tag_from = Tag.objects.first()
        tag_to = save_doubled_tag(tag_from)
        self.assertNotEqual(tag_from.slug, tag_to.slug)
