# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-04 09:54
from __future__ import unicode_literals

from django.db import migrations


def migrate_forward(apps, schema_editor):
    MatrixBlock = apps.get_model('shopelectro', 'MatrixBlock')
    Category = apps.get_model('shopelectro', 'Category')

    for c in Category.objects.filter(level=0):
        MatrixBlock.objects.get_or_create(category=c)


def migrate_backward(apps, schema_editor):
    MatrixBlock = apps.get_model('shopelectro', 'MatrixBlock')
    MatrixBlock.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0036_matrixblock'),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_backward),
    ]
