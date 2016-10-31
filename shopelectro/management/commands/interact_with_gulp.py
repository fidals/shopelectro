from django.apps import apps
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            nargs='+',
            type=str,
        )


    def handle(self, *args, **options):
        assert options['app_name'], 'You need to pass at least one app_name in arguments'
        app_paths = [
            app_config.path
            for app_name, app_config in apps.app_configs.items()
            if app_name in options['app_name']
        ]
        assert app_paths, 'Incorrect arguments'
        self.stdout.write(';'.join(app_paths))
