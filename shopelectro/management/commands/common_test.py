import os
import subprocess
import sys

from django.core import management
from django.core.management.base import BaseCommand, CommandError

import pages
import catalog
import ecommerce


class Command(BaseCommand):
    """Runs tests for project and for every refarm-* application."""

    def handle(self, *args, **options):
        try:
            management.call_command('test')
        except CommandError as err:
            print(err)

        for app in (pages, catalog, ecommerce):
            path2test = os.path.dirname(os.path.dirname(app.__file__))
            test_name = 'runtests.py'
            subprocess.call(
                [sys.executable, os.path.join(path2test, test_name)],
                stdout=self.stdout, stderr=self.stderr)
