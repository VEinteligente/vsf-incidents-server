# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-29 20:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('measurement', '0007_flag_suggested_events'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flag',
            name='suggested_events',
            field=models.ManyToManyField(blank=True, related_name='suggested_events', to='event.Event'),
        ),
    ]