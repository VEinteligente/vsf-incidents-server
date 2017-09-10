# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-23 20:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('abbreviation', models.CharField(max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('identification', models.CharField(max_length=50, unique=True)),
                ('draft', models.BooleanField(default=True)),
                ('public_evidence', models.TextField(blank=True, null=True)),
                ('private_evidence', models.TextField(blank=True, null=True)),
                ('type', models.CharField(choices=[('bloqueo por DPI', 'bloqueo por DPI'), ('bloqueo por DNS', 'bloqueo por DNS'), ('bloqueo por IP', 'bloqueo por IP'), ('Interceptacion de trafico', 'Interceptaci\xf3n de tr\xe1fico'), ('falla de dns', 'falla de dns'), ('Velocidad de internet', 'Velocidad de internet'), ('alteracion de trafico por intermediarios', 'alteraci\xf3n de tr\xe1fico por intermediarios')], max_length=100)),
                ('plugin_name', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ISP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MutedInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=50, null=True)),
                ('type_med', models.CharField(choices=[('MED', 'Medicion'), ('DNS', 'Medicion DNS'), ('TCP', 'Medicion TCP'), ('HTTP', 'Medicion HTTP')], default='MED', max_length=50, verbose_name='Tipo de Medicion')),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('upload', models.CharField(max_length=30, verbose_name='Velocidad de Carga publicitado')),
                ('download', models.CharField(max_length=30, verbose_name='Velocidad de Descarga publicitado')),
                ('comment', models.TextField(blank=True, null=True)),
                ('isp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.ISP')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SiteCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('abbreviation', models.CharField(blank=True, max_length=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='event.Country')),
            ],
            options={
                'verbose_name': 'State',
                'verbose_name_plural': 'States',
            },
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(blank=True, max_length=100, null=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('type', models.CharField(choices=[('domain', 'Domain'), ('url', 'Url'), ('ip', 'Ip')], default='domain', max_length=10)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='targets', to='event.Site')),
            ],
        ),
        migrations.AddField(
            model_name='site',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='event.SiteCategory'),
        ),
        migrations.AddField(
            model_name='event',
            name='isp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='event.ISP'),
        ),
        migrations.AddField(
            model_name='event',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='event.State'),
        ),
        migrations.AddField(
            model_name='event',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.Target'),
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([('name', 'country')]),
        ),
    ]
