# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-02 15:37
# TODO need squashing this migration https://goo.gl/aohgCq
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopelectro', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='spam_text',
        ),
    ]
