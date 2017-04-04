from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.urls import reverse

from shopelectro.models import Product


def create():
    site = Site.objects.get(id=settings.SITE_ID)

    for product in Product.objects.all():
        if product.id != product.vendor_code:
            Redirect.objects.create(
                site=site,
                old_path=reverse('product', args=(product.id,)),
                new_path=product.url
            )


class Command(BaseCommand):

    def handle(self, *args, **options):
        create()
