import os
import unittest

from django.test import TestCase, tag
from django.conf import settings
from django.template.loader import render_to_string

from html5validate import validate


@tag('fast')
class TemplateTests(TestCase):

    @unittest.skip
    def test_templates(self):
        for dir, _, filenames in os.walk(settings.TEMPLATE_DIR):
            for filename in filenames:
                filepath = os.path.join(dir, filename)
                filename, file_ext = os.path.splitext(filepath)
                if file_ext == '.html':
                    validate(render_to_string(filepath))

    def test_valid_example(self):
        validate(render_to_string('/usr/app/src/templates/valid_example.html'))
