# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-29 14:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0028_create_order_revenue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(db_index=True, max_length=1000, verbose_name='name'),
        ),
    ]
