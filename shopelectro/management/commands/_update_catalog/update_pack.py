import logging

from django.db import transaction

from shopelectro.models import TagGroup

logger = logging.getLogger(__name__)


def main(*args, kwargs):
    uuid = 'ae30f766-0bb8-11e6-80ea-02d2cc20e118'
    pack_group = TagGroup.objects.filter(uuid=uuid).first()
    if not pack_group:
        logger.error(f'Couldn\'t find "Упаковка" tag group with uuid = "{uuid}".')
        return

    # @todo #827:60m Update Product.in_pack and render prices properly.

    return
    packs = pack_group.tags.all().prefetch_related('products')
    with transaction.atomic():
        for pack in packs:
            ...
