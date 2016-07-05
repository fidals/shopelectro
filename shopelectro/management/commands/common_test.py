import os
import subprocess

from django.core.management.base import BaseCommand
from django.core import management
from django.core.management.base import CommandError

import catalog
import ecommerce
import blog
import seo


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            management.call_command('tests')
        except CommandError as err:
            print(err)

        for app in (catalog, blog, ecommerce, seo):
            path2test = os.path.dirname(os.path.dirname(app.__file__))
            test_name = 'runtests.py'
            subprocess.call(['python', os.path.join(path2test, test_name)], stdout=self.stdout, stderr=self.stderr)
