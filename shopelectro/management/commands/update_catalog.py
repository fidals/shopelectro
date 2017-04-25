import time

import requests
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
            self.report(err)
            raise err

    @staticmethod
    def update(*args, **kwargs):
        with utils.download_catalog(destination=settings.ASSETS_DIR):
            start = time.time()
            update_tags.main(*args, **kwargs)
            update_products.main(*args, **kwargs)
            print('Time elapsed {:.2f}.'.format(time.time() - start))

    @staticmethod
    def report(error):
        report_url = getattr(settings, 'SLACK_REPORT_URL', None)
        if report_url is not None:
            requests.post(
                url=report_url,
                json={
                    'text': '*Неудалось обновить каталог Shopelectro.*\n'
                            '*Время*: {}\n'
                            '*Ошибка*: {}'.format(time.ctime(), error),
                    'icon_emoji': ':octopus:',

                }
            )
