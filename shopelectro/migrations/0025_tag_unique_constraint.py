# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-24 08:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0024_update_robots_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(default='', unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=['name', 'group'],
        ),
    ]
