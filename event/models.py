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


class MutedInput(models.Model):

    MED = 'MED'
    DNS = 'DNS'
    TCP = 'TCP'
    HTTP = 'HTTP'

    TYPE_CHOICES = (
        (MED, 'Medicion'),
        (DNS, 'Medicion DNS'),
        (TCP, 'Medicion TCP'),
        (HTTP, 'Medicion HTTP')
    )

    url = models.CharField(max_length=50, null=True)
    type_med = models.CharField(verbose_name='Tipo de Medicion',
                                max_length=50,
                                choices=TYPE_CHOICES,
                                default=MED)

    def __unicode__(self):
        return u"%s - %s" % (self.url, self.type_med)


class ISP(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s" % self.name


class Plan(models.Model):
    name = models.CharField(max_length=100)
    isp = models.ForeignKey(ISP)
    upload = models.CharField(
        verbose_name='Velocidad de Carga publicitado',
        max_length=30)
    download = models.CharField(
        verbose_name='Velocidad de Descarga publicitado',
        max_length=30)
    comment = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.name


class SiteCategory(models.Model):

    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    abbreviation = models.CharField(max_length=5, null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.name


class Site(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(SiteCategory, null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.name


class Target(models.Model):

    SITE = 'site'
    URL = 'url'
    IP = 'ip'

    TYPE = (
        (SITE, 'Site'),
        (URL, 'Url'),
        (IP, 'Ip')
    )

    site = models.ForeignKey(Site, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    type = models.CharField(choices=TYPE, default=SITE, max_length=5)

    def __unicode__(self):

        if self.type == self.SITE:
            return u"%s -> %s" % (self.type, self.site)
        elif self.type == self.URL:
            return u"%s -> %s" % (self.type, self.url)
        elif self.type == self.IP:
            return u"%s -> %s" % (self.type, self.ip)


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

    isp = models.ForeignKey(ISP, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    target = models.ForeignKey(Target)  # input in metrics
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
