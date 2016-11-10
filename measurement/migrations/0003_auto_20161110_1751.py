# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-10 17:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('measurement', '0002_auto_20161108_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='flag',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='flag',
            name='isp',
            field=models.CharField(default=' ', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='flag',
            name='target',
            field=models.CharField(default=' ', max_length=100),
            preserve_default=False,
        ),
    ]
