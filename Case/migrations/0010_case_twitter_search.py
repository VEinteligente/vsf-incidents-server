# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-10 14:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Case', '0009_auto_20161221_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='twitter_search',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]
