from django.test import TestCase, override_settings, tag

from pages import models as pages_models
from shopelectro import models, logic


@tag('fast')
@override_settings(HEADER_LINKS={'exclude': [], 'add': []})
class HeaderMenu(TestCase):
    fixtures = ['dump.json']
    to_exclude = models.CategoryPage.objects.get_cached_trees()[0]
    to_add = pages_models.CustomPage.objects.get(slug='catalog')

    def test_roots_are_presented(self):
        from_db = set(models.CategoryPage.objects.get_cached_trees())
        from_logic = set(logic.header.Menu().as_dict().keys())
        self.assertEqual(from_db, from_logic)

    def test_children_contains_no_products(self):
        root = models.CategoryPage.objects.get_cached_trees()[0]
        product = models.ProductPage.objects.first()
        product.parent = root
        product.save()
        children = logic.header.Menu().as_dict()[root]
        self.assertNotIn(product, children)

    @override_settings(HEADER_LINKS={'exclude': [to_exclude.slug], 'add': []})
    def test_exclude_option(self):
        self.assertNotIn(self.to_exclude, logic.header.Menu().as_dict().keys())

    @override_settings(HEADER_LINKS={'exclude': [], 'add': [to_add.slug]})
    def test_add_option(self):
        self.assertIn(self.to_add, logic.header.Menu().as_dict().keys())
