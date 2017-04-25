# coding=utf-8
from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=50, null=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return u'%s' % self.name

    def __unicode__(self):
        return u'%s' % self.name


class State(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, related_name='states')

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"

    def __str__(self):
        return u'%s' % self.name

    def __unicode__(self):
        return u'%s' % self.name


class Site(models.Model):

    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s" % self.name


class Url(models.Model):

    site = models.ForeignKey(Site, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    def __unicode__(self):
        return u"%s@%s - ip:%s" % (self.site, self.url, self.ip)


class Event(models.Model):

    NONE = 'none'
    TCP = 'tcp'
    DNS = 'dns'
    HTTP = 'http'
    NDT = 'ndt'

    TYPE = {
        NONE: 'none',
        TCP: 'tcp',
        DNS: 'dns',
        HTTP: 'http',
        NDT: 'ndt'
    }

    TYPE_CHOICES = [    # Items are sorted alphabetically
        (k, v) for k, v in sorted(TYPE.items(), key=lambda t: t[1])]

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
    target = models.ForeignKey(Url)  # input in metrics
    region = models.ForeignKey(State, null=True, blank=True)
    identification = models.CharField(max_length=50, unique=True)
    draft = models.BooleanField(default=True)
    public_evidence = models.TextField(null=True, blank=True)
    private_evidence = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, choices=TYPES)
    plugin_name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        return super(Event, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                       update_fields=update_fields)

    def __unicode__(self):
        return u"%s" % self.identification
