# coding=utf-8
from __future__ import unicode_literals

from django.db import models
# from Case.models import Case


class Event(models.Model):

    TYPES = (
        ('bloqueo por DPI', 'bloqueo por DPI'),
        ('bloqueo por DNS', 'bloqueo por DNS'),
        ('bloqueo por IP', 'bloqueo por IP'),
        ('Interceptacion de trafico', 'Interceptación de tráfico'),
        ('falla de dns', 'falla de dns'),
        ('Velocidad de internet', 'Velocidad de internet'),
        ('alteracion de trafico por intermediarios', 'alteración de tráfico por intermediarios')
    )

    isp = models.CharField(max_length=25)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    target = models.CharField(max_length=25)  # input in metrics
    identification = models.CharField(max_length=50)
    draft = models.BooleanField(default=True)
    type = models.CharField(max_length=100, choices=TYPES)
    # case = models.ForeignKey(Case)
