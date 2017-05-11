# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

# https://goo.gl/5qYGp1
flag_symbol = '\U0001F6A9'


def migrate_forward(apps, schema_editor):
    PageTemplate = apps.get_model('pages', 'PageTemplate')

    category_template = PageTemplate.objects.create(
        name='Шаблон страницы категории',
        title='{{ page.name }} - купить в интернет-магазине - ShopElectro',
        h1='{{ page.name }}',
        seo_text='Наши цены ниже, чем у конкурентов, потому что мы покупаем напрямую у производителя.'
    )

    product_template = PageTemplate.objects.create(
        name='Шаблон страницы продукта',
        title='{{ page.name }} - купить недорого оптом, со скидкой в интернет-магазине ShopElectro в СПб, цена - {{ page.model.price }} руб',
        description='{{ page.name }} - Элементы питания, зарядные устройства, ремонт. Купить {{ page.model.category.name }} в Санкт-Петербурге.',
        h1='{{ page.name }}',
    )

    Category = apps.get_model('shopelectro', 'CategoryPage')
    Product = apps.get_model('shopelectro', 'ProductPage')

    Category.objects.filter(template_id=1).update(template=category_template)

    Product.objects.filter(template_id=1).update(template=product_template)


def migrate_backward(apps, schema_editor):
    PageTemplate = apps.get_model('pages', 'PageTemplate')
    Category = apps.get_model('shopelectro', 'CategoryPage')
    Product = apps.get_model('shopelectro', 'ProductPage')

    Category.objects.update(template_id=1)
    Product.objects.update(template_id=1)

    PageTemplate.objects.filter(name__in=[
        'Шаблон страницы категории',
        'Шаблон страницы продукта',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0018_product_vendor_code'),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_backward)
    ]
