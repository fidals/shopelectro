"""
Views tests.

Note: there should be tests, subclassed from TestCase.
They all should be using Django's TestClient.

All Selenium-tests should live in tests_selenium.
"""
from xml.etree import ElementTree as ET

from django.core.management import call_command
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class SitemapPage(TestCase):
    """
    Tests for Sitemap.
    Getting sitemap.xml and parsing it as string.
    """

    fixtures = ['dump.json']

    @classmethod
    def setUpTestData(cls):
        """Import testing data into DB and create site domain name."""
        call_command('redirects')

        # Namespace for using ET.find()
        cls.NAMESPACE = '{http://www.sitemaps.org/schemas/sitemap/0.9}'

    def setUp(self):
        """Sets up testing url."""

        content = self.client.get('/sitemap.xml').content.decode('utf-8')
        self.root = ET.fromstring(content)

    def test_url_tags(self):
        """We should see <url> tags on Sitemap page."""
        url_tags = self.root.findall('{}url'.format(self.NAMESPACE))
        self.assertGreater(len(url_tags), 0)

    def test_models_urls(self):
        """Sitemap page should to print correct urls for models."""
        slice_start_index = len('http://' + settings.SITE_DOMAIN_NAME)

        path = '{0}url[2]/{0}loc'.format(self.NAMESPACE)
        model_url_text = self.root.find(path).text[slice_start_index:]

        response = self.client.get(model_url_text)

        self.assertEqual(response.status_code, 200)


class AdminPage(TestCase):
    """Tests for Admin page UI."""

    fixtures = ['dump.json']

    def setUp(self):
        self.username = 'admin'
        self.email = 'admin@admin.com'
        self.password = 'asdfjkl'
        self.user = User.objects.create_superuser(self.username, self.email, self.password)
        self.client.login(username=self.username, password=self.password)

    def tearDown(self):
        self.user.delete()

    def test_model_fieldsets(self):
        """Models should has fields printed in 3 fieldset groups."""

        response = self.client.get(reverse('admin:shopelectro_product_change', args=(1,)))
        page_body = response.content.decode('utf-8')

        self.assertTrue('Основные характеристики' in page_body)
        self.assertTrue('Дополнительные характеристики' in page_body)
        self.assertTrue('SEO' in page_body)
