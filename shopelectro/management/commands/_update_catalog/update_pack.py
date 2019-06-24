"""
Update Product.in_pack and prices.

The update_catalog command always resets product prices to per unit format, so:
1. Parse in pack quantity from Tag.name and save it to Product.in_pack
2. Multiply product prices by in_pack value and save.
"""
import logging
import typing

from django.conf import settings
from django.db import models, transaction

from catalog.models_expressions import Substring

from shopelectro.models import TagQuerySet, TagGroup

logger = logging.getLogger(__name__)
PRICES = ['price', 'purchase_price', 'wholesale_small', 'wholesale_medium', 'wholesale_large']


def find_pack_group() -> typing.Optional[TagGroup]:
    pack_group = TagGroup.objects.filter(uuid=settings.PACK_GROUP_UUID).first()

    # @todo #864:60m Raise errors in find_pack_group.
    #  Remove Optional type as returning value and test find_pack_group.
    if not pack_group:
        logger.error(
            f'Couldn\'t find "{settings.PACK_GROUP_NAME}" tag group by UUID="{settings.PACK_GROUP_UUID}".\n'
            'Update the PACK_GROUP_UUID environ variable to set the new relevant UUID.'
        )
        pack_group = None
    if not settings.PACK_GROUP_NAME.lower() not in pack_group.name.lower():
        logger.error(
            'The pack group name isn\'t matched with the set name:'
            f' Pack group name: {pack_group.name}\n'
            f' Set name: {settings.PACK_GROUP_NAME}\n'
            'Update the PACK_GROUP_NAME environ variable to set the new relevant name.'
        )
        pack_group = None

    return pack_group


def update_in_packs(packs: TagQuerySet):
    """Parse and save in pack quantity values."""
    packs = (
        packs
        .annotate(
            in_pack_str=Substring(
                models.F('name'),
                models.Value('[0-9]+\+?[0-9]*')))
        .exclude(in_pack_str__exact='')
    )

    for pack in packs:
        in_pack = sum(map(int, pack.in_pack_str.split('+')))
        pack.products.all().update(in_pack=max(in_pack, 1))


def update_prices(packs: TagQuerySet):
    """Multiply product prices on in pack quantity."""
    fields_to_update = {}
    for price in PRICES:
        fields_to_update[price] = models.F(price) * models.F('in_pack')

    with transaction.atomic():
        packs.products().update(**fields_to_update)


def main(*args, **kwargs):
    pack_group = find_pack_group()
    if not pack_group:
        return

    return

    packs = pack_group.tags.all().prefetch_related('products')
    update_in_packs(packs)
    update_prices(packs)
