from django.test import override_settings, TestCase

from shopelectro.models import Category
from shopelectro.templatetags.se_extras import roots


class TemplateTags(TestCase):

    fixtures = ['dump.json']

    def test_root_categories(self):
        """All root categories are presence in the `roots` tag."""
        self.assertFalse(
            set(Category.objects.get_cached_trees()) ^ set(roots()),
        )

    def test_exclusions_of_root_categories(self):
        """Excluded categories are not presence in the `roots` tag."""
        excluded_category, _ = categories = Category.objects.get_cached_trees()
        excluded_category.page.is_active = False
        excluded_category.page.save()

        self.assertTrue(
            excluded_category in set(categories) ^ set(roots())
        )
