"""
Update Product.in_pack and prices.

The update_catalog command always resets product prices to per unit format, so:
1. Parse in pack quantity from Tag.name and save it to Product.in_pack
2. Multiply product prices by in_pack value and save.
"""
import logging

from django.db import models, transaction

from shopelectro.models import TagQuerySet, TagGroup

logger = logging.getLogger(__name__)
PRICES = ['price', 'purchase_price', 'wholesale_small', 'wholesale_medium', 'wholesale_large']


def update_in_packs(packs: TagQuerySet):
    """Parse and save in pack quantity values."""
    # @todo #859:60m Implement update_pack and render prices properly.


def update_prices(packs: TagQuerySet):
    """Multiply product prices on in pack quantity."""
    fields_to_update = {}
    for price in PRICES:
        fields_to_update[price] = models.F(price) * models.F('in_pack')

    with transaction.atomic():
        packs.products().update(**fields_to_update)


def main(*args, kwargs):
    uuid = 'ae30f766-0bb8-11e6-80ea-02d2cc20e118'
    pack_group = TagGroup.objects.filter(uuid=uuid).first()
    if not pack_group:
        logger.error(f'Couldn\'t find "Упаковка" tag group with uuid = "{uuid}".')
        return

    return

    packs = pack_group.tags.all().prefetch_related('products')
    update_in_packs(packs)
    update_prices(packs)
