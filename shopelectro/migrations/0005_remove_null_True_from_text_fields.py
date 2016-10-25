# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-10 14:26
from __future__ import unicode_literals

from django.db import migrations


def remove_null_fields(apps, schema_editor):
    """
    Char and Text fields should be null=False.
    https://goo.gl/8t54Ln
    """
    db_alias = schema_editor.connection.alias
    Page = apps.get_model('pages', 'Page').objects.using(db_alias)

    null_fields = ['_menu_title', 'content', 'seo_text']
    for null_field in null_fields:
        pages = Page.filter(**{null_field: None})
        pages.update(**{null_field: ''})


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0004_add_yandex_payment_types'),
    ]

    run_before = [
        ('pages', '0005_db_refactor')
    ]

    operations = [
        migrations.RunPython(remove_null_fields)
    ]
