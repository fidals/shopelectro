from django.test import TestCase, override_settings, tag

from shopelectro import models, logic


@tag('fast')
@override_settings(HEADER_LINKS={'exclude': [], 'add': []})
class HeaderMenu(TestCase):
    fixtures = ['dump.json']

    def test_roots_are_presented(self):
        from_db = set(models.CategoryPage.objects.get_cached_trees())
        from_logic = set(logic.header.menu_qs())
        self.assertEqual(from_db, from_logic)
