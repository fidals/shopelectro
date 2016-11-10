"""
Module version: dev-811
Purge call_command: after dev-811 task release

Module with command for autodeploy one particular release.
Put here only calls of other commands.
If you have not command for current release, just leave Command.handle method empty.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        call_command('catalog')
        call_command('images')
        call_command('collectstatic', '--noinput')
