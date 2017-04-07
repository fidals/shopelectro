import time

from django.core.management.base import BaseCommand
from django.conf import settings

from shopelectro.management.commands._update_catalog import (
    utils, update_tags, update_products, update_meta_tags
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipients',
            nargs='+',
            default=[],
            help='Send an email to recipients if products will be created.',
        )

    def handle(self, *args, **options):
        with utils.download_catalog(destination=settings.ASSETS_DIR):
            start = time.time()
            update_tags.main(*args, **options)
            update_products.main(*args, **options)
            update_meta_tags.main(*args, **options)
            print('Time elapsed {:.2f}.'.format(time.time() - start))
