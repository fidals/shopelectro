import unittest

from django.test import TestCase, override_settings, tag

from pages import models as pages_models
from shopelectro import models, logic


@tag('fast')
@override_settings(HEADER_LINKS={'exclude': [], 'add': []})
class HeaderMenu(TestCase):
    fixtures = ['dump.json']
    to_exclude = (
        models.CategoryPage.objects.get_cached_trees()[0]
        .get_children().first()
    )
    to_add = pages_models.CustomPage.objects.get(slug='catalog')

    def test_roots_are_presented(self):
        from_db = set(models.CategoryPage.objects.get_cached_trees())
        from_logic = set(logic.header.menu_qs())
        self.assertEqual(from_db, from_logic)

    # @todo #980:30m  Fix top_menu "exclude" logic
    @unittest.expectedFailure
    @override_settings(HEADER_LINKS={'exclude': [to_exclude.slug], 'add': []})
    def test_exclude_option(self):
        for root in logic.header.menu_qs().iterator():
            self.assertNotIn(self.to_exclude, root.get_children())

    @override_settings(HEADER_LINKS={'exclude': [], 'add': [to_add.slug]})
    def test_add_option(self):
        self.assertIn(self.to_add, logic.header.menu_qs())
