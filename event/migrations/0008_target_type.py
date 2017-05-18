# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-05-17 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0007_auto_20170510_2030'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='type',
            field=models.CharField(choices=[('site', 'Site'), ('url', 'Url'), ('ip', 'Ip')], default='site', max_length=5),
        ),
    ]
