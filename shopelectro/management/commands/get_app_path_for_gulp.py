"""Write path in stdout for given app"""
from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            type=str,
        )

    def handle(self, *args, **options):
        assert options['app_name'], 'You need to pass app_name in arguments'
        app_paths = apps.app_configs[options['app_name']].path
        self.stdout.write(app_paths)
