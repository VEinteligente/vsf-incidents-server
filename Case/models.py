from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from datetime import date as d

from event.models import Event


class Category(models.Model):
    name = models.CharField(max_length=30)
    display_name = models.CharField(max_length=50)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Case(models.Model):

    TYPE_CATEGORIES = (
        ('bloqueo', 'Bloqueo'),
        ('desconexion', 'Desconexion'),
        ('relentizacion', 'Relentizacion de servicio en Linea'),
        ('conexion', 'Conexion inusualmente lenta'),
        ('intercepcion', 'Intercepcion de trafico'),
        ('falla', 'Falla Importante'),
        ('dos', 'DoS')
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    category = models.ForeignKey(   to=Category, 
                                    on_delete=models.CASCADE, #FOR DEBUG ONLY @TODO
                                    related_name="cases")
    draft = models.BooleanField(default=True)
    events = models.ManyToManyField(Event, related_name="cases")
    twitter_search = models.CharField(max_length=400, null=True, blank=True)


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
    case = models.ForeignKey(   to=Case, 
                                on_delete=models.CASCADE, #FOR DEBUGGING, CHECK LATER @TODO
                                related_name="updates")
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, #FOR DEBUGGING, CHECK LATER @TODO
        related_name='updates',
        null=True, blank=True
    )
    created = models.DateField(default=d.today)

    def __unicode__(self):
        return u"%s" % self.title
