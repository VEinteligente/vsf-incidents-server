from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from datetime import date as d

from event.models import Event


class Case(models.Model):

    TYPE_CATEGORIES = (
        ('bloqueo', 'Bloqueo'),
        ('desconexion', 'Desconexion'),
        ('relentizacion', 'Relentizacion de servicio en Linea'),
        ('conexion', 'Conexion inusualmente lenta'),
        ('interceptacion', 'Interceptacion de trafico'),
        ('falla', 'Falla Importante'),
        ('dos', 'DoS')
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    category = models.CharField(choices=TYPE_CATEGORIES, max_length=20)
    draft = models.BooleanField(default=True)
    events = models.ManyToManyField(Event, related_name="cases")


class Update(models.Model):
    TYPE = (
        ('info', 'Info'),
        ('grave', 'Grave'),
        ('positivo', 'Positivo')
    )

    date = models.DateField()
    title = models.CharField(max_length=100)
    text = models.TextField()
    category = models.CharField(choices=TYPE, max_length=20)
    case = models.ForeignKey(Case, related_name="updates")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='updates',
        null=True, blank=True
    )
    created = models.DateField(default=d.today)

    def __unicode__(self):
        return u"%s" % self.title
