from django.test import TestCase, tag

from shopelectro.models import CategoryPage
from shopelectro.templatetags.se_extras import roots


@tag('fast')
class TemplateTags(TestCase):

    fixtures = ['dump.json']

    def test_root_categories(self):
        """All root categories are presented in result of calling the `roots` tag."""
        self.assertFalse(
            set(CategoryPage.objects.get_cached_trees()) ^ set(roots()),
        )

    def test_exclusions_of_root_categories(self):
        """Excluded categories are not presented in result of calling the `roots` tag."""
        excluded_category, *_ = categories = CategoryPage.objects.get_cached_trees()
        excluded_category.is_active = False
        excluded_category.save()

        self.assertTrue(
            excluded_category in set(categories) ^ set(roots())
        )
