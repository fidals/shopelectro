# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-02-20 02:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0031_buff_tag_name'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ExcludedModelTPage',
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('slug', 'group'), ('name', 'group')]),
        ),
    ]