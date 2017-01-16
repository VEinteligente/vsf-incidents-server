# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-10 17:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Case', '0009_auto_20161221_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='category_de',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cases', to='Case.Category'),
        ),
        migrations.AddField(
            model_name='case',
            name='category_es',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cases', to='Case.Category'),
        ),
        migrations.AddField(
            model_name='case',
            name='description_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='case',
            name='description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='case',
            name='title_de',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='case',
            name='title_es',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='display_name_de',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='display_name_es',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
