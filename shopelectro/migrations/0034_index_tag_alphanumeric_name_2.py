# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-02-21 23:49
from __future__ import unicode_literals

from django.db import migrations

from catalog.models_operations import IndexTagAlphanumeric


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0033_index_tag_alphanumeric_name'),
    ]

    operations = IndexTagAlphanumeric().v2()
