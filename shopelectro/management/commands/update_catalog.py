import time

from django.core.management.base import BaseCommand
from django.conf import settings

from shopelectro.management.commands._update_catalog import (
    utils, update_tags, update_products,
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipients',
            nargs='+',
            default=[],
            help='Send an email to recipients if products will be created.',
        )

    def handle(self, *args, **kwargs):
        try:
            self.update(*args, **kwargs)
        except Exception as err:
            utils.report(err)
            raise err

    @staticmethod
    def update(*args, **kwargs):
        with utils.download_catalog(destination=settings.ASSETS_DIR):
            with utils.collect_errors() as (collect_error, errors):
                start = time.time()
                with collect_error():
                    update_tags.main(*args, **kwargs)
                with collect_error():
                    update_products.main(*args, **kwargs)
                if errors:
                    raise errors[0]
                print('Time elapsed {:.2f}.'.format(time.time() - start))
