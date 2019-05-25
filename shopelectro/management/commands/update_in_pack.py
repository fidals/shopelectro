import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from shopelectro.models import TagGroup

logger = logging.getLogger(__name__)


def update():
    uuid = 'ae30f766-0bb8-11e6-80ea-02d2cc20e118'
    pack_group = TagGroup.objects.filter(uuid=uuid).first()
    if not pack_group:
        logger.error(f'Couldn\'t find "Упаковка" tag group with uuid = "{uuid}".')
        return

    # @todo #827:60m Update Product.in_pack and render prices properly.

    packs = pack_group.tags.all().prefetch_related('products')
    with transaction.atomic():
        for pack in packs:
            ...


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        update()
