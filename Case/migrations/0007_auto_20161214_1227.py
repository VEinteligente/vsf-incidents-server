# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-14 12:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Case', '0006_auto_20161213_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='category',
            field=models.CharField(choices=[('bloqueo', 'Bloqueo'), ('desconexion', 'Desconexion'), ('relentizacion', 'Relentizacion de servicio en Linea'), ('conexion', 'Conexion inusualmente lenta'), ('intercepcion', 'Intercepcion de trafico'), ('falla', 'Falla Importante'), ('dos', 'DoS')], max_length=20),
        ),
    ]
