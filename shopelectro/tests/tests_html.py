import os
import unittest

from django.test import TestCase, tag
from django.conf import settings
from django.template.loader import render_to_string

from html5validate import validate
from html5lib import html5parser


@tag('fast')
class TemplateTests(TestCase):

    @unittest.skip('should fix html templates')
    def test_templates(self):
        for dir, _, filenames in os.walk(settings.TEMPLATE_DIR):
            for filename in filenames:
                filepath = os.path.join(dir, filename)
                filename, file_ext = os.path.splitext(filepath)
                if file_ext == '.html':
                    validate(render_to_string(filepath))

    def test_valid_example(self):
        filepath = os.path.join(
            settings.TEMPLATE_ASSETS_DIR,
            'valid_markup_example.html'
        )
        validate(render_to_string(filepath))

    #@unittest.expectedFailure
    def test_invalid_example(self):
        filepath = os.path.join(
            settings.TEMPLATE_ASSETS_DIR,
            'invalid_markup_example.html'
        )
        with self.assertRaises(html5parser.ParseError):
            validate(render_to_string(filepath))
