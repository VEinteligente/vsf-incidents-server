# coding=utf-8
from __future__ import unicode_literals

from django.db import models


class Site(models.Model):

    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s" % self.name


class Url(models.Model):

    site = models.ForeignKey(
                        Site, 
                        on_delete=models.CASCADE, #FOR TESTING PURPOSE ONLY @TODO
                        null=True, 
                        blank=True)

    url = models.URLField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    def __unicode__(self):
        return u"%s@%s - ip:%s" % (self.site, self.url, self.ip)


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
    target = models.ForeignKey( to=Url, # input in metrics
                                on_delete=models.CASCADE)  # ONLY DEBUGGING
    identification = models.CharField(max_length=50, unique=True)
    draft = models.BooleanField(default=True)
    public_evidence = models.TextField(null=True, blank=True)
    private_evidence = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, choices=TYPES)

    def __unicode__(self):
        return u"%s" % self.identification
