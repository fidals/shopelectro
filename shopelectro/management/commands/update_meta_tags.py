from django.core.management.base import BaseCommand
from django.db import transaction

from pages.models import PageTemplate
from shopelectro.models import ProductPage, CategoryPage


@transaction.atomic
def update():

    # select category & product pages with default page template
    categories = CategoryPage.objects.filter(template_id=1)
    products = ProductPage.objects.filter(template_id=1)

    # select default category and product page templates
    category_template = PageTemplate.objects.get(name='Шаблон страницы категории')
    product_template = PageTemplate.objects.get(name='Шаблон страницы продукта')

    categories.update(template=category_template)
    products.update(template=product_template)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        update()
