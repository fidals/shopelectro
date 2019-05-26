import logging
import time

from django.core.management.base import BaseCommand
from django.conf import settings

from shopelectro.management.commands._update_catalog import (
    utils, update_tags, update_products, update_pack,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipients',
            nargs='+',
            default=[],
            help='Send an email to recipients if products will be created.',
        )

    def handle(self, *args, **kwargs):
        self.update(*args, **kwargs)

    @staticmethod
    def update(*args, **kwargs):
        with utils.download_catalog(destination=settings.ASSETS_DIR):
            with utils.collect_errors(
                (AssertionError, update_products.UpdateProductError)
            ) as collect_error:
                start = time.time()
                with collect_error():
                    update_tags.main(*args, **kwargs)
                with collect_error():
                    update_products.main(*args, **kwargs)
                with collect_error():
                    update_pack.main(*args, **kwargs)
                logger.info('Time elapsed {:.2f}.'.format(time.time() - start))
