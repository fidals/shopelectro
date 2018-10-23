# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-02 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0027_increase_h1_name_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='revenue',
            field=models.FloatField(default=0, verbose_name='revenue'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(db_index=True, max_length=255, verbose_name='name'),
        ),
    ]