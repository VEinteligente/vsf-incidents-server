# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-16 22:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('measurement', '0004_flag_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flag',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='flags', to='event.Event'),
        ),
    ]