from __future__ import unicode_literals

from django.db import models
from event.models import Event, Url


class Metric(models.Model):

    _DATABASE = 'titan_db'
    manage = False

    # Test name helper: dns_consistency web_connectivity http_header_field_manipulation http_invalid_request_line

    input = models.CharField(max_length=50)
    annotations = models.TextField()
    report_id = models.CharField(max_length=100)
    report_filename = models.CharField(max_length=150)
    options = models.TextField()
    probe_cc = models.CharField(max_length=50)
    probe_asn = models.CharField(max_length=50)
    probe_ip = models.GenericIPAddressField()
    data_format_version = models.CharField(max_length=10)
    test_name = models.CharField(max_length=25)
    test_start_time = models.DateTimeField()
    measurement_start_time = models.DateTimeField()
    test_runtime = models.FloatField()
    test_helpers = models.TextField()
    test_keys = models.TextField()
    software_name = models.CharField(max_length=15)
    software_version = models.CharField(max_length=10)
    test_version = models.CharField(max_length=10)
    bucket_date = models.DateTimeField()

    class Meta:
        db_table = 'metrics'

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

    url = models.URLField()
    type_med = models.CharField(verbose_name='Tipo de Medicion',
                                max_length=50,
                                choices=TYPE_CHOICES,
                                default=MED)

    def __unicode__(self):
        return u"%s - %s" % (self.url, self.type_med)


class Plan(models.Model):
    name = models.CharField(max_length=100)
    isp = models.CharField(max_length=100)
    upload = models.CharField(
        verbose_name='Velocidad de Carga publicitado',
        max_length=30)
    download = models.CharField(
        verbose_name='Velocidad de Descarga publicitado',
        max_length=30)
    comment = models.TextField(null=True, blank=True)


class Probe(models.Model):
    STATES_CHOICES = (
        ('amazonas', 'Amazonas'),
        ('anzoategui', 'Anzoategui'),
        ('apure', 'Apure'),
        ('aragua', 'Aragua'),
        ('barinas', 'Barinas'),
        ('bolivar', 'Bolivar'),
        ('carabobo', 'Carabobo'),
        ('cojedes', 'Cojedes'),
        ('delta_amacuro', 'Delta Amacuro'),
        ('distrito_capital', 'Distrito Capital'),
        ('falcon', 'Falcon'),
        ('guarico', 'Guarico'),
        ('lara', 'Lara'),
        ('merida', 'Merida'),
        ('miranda', 'Miranda'),
        ('monagas', 'Monagas'),
        ('nueva_esparta', 'Nueva Esparta'),
        ('portuguesa', 'Portuguesa'),
        ('sucre', 'Sucre'),
        ('tachira', 'Tachira'),
        ('trujillo', 'Trujillo'),
        ('vargas', 'Vargas'),
        ('yaracuy', 'Yaracuy'),
        ('zulia', 'Zulia')
    )

    COUNTRIES_CHOICES = (
        ('venezuela', 'Venezuela'),
    )
    identification = models.CharField(max_length=50)
    region = models.CharField(
        max_length=50,
        choices=STATES_CHOICES,
        default='distrito_capital'
    )
    country = models.CharField(
        max_length=50,
        choices=COUNTRIES_CHOICES,
        default='venezuela'
    )
    city = models.CharField(max_length=100)
    isp = models.CharField(max_length=100)
    plan = models.ForeignKey(
        Plan, null=True, blank=True, related_name='probes')


class DNS(models.Model):

    isp = models.CharField(verbose_name='Operadora', max_length=50)
    verbose = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    public = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s - %s" % (self.verbose, self.ip)


class Flag(models.Model):

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

    medicion = models.CharField(verbose_name='Id de la Medicion',
                                max_length=40)
    date = models.DateTimeField()
    target = models.ForeignKey(Url)
    isp = models.CharField(max_length=100)
    probe = models.ForeignKey(
        Probe, null=True, blank=True, related_name='flags')
    ip = models.GenericIPAddressField()
    # True -> hard, False -> soft, None -> muted
    flag = models.NullBooleanField(default=False)
    type_med = models.CharField(verbose_name='Tipo de Medicion',
                                max_length=50,
                                choices=TYPE_CHOICES,
                                default=MED)
    event = models.ForeignKey(Event, null=True, blank=True,
                              related_name='flags')
    suggested_events = models.ManyToManyField(
        Event, related_name="suggested_events", blank=True)

    def __unicode__(self):
        return u"%s - %s - %s" % (self.medicion, self.ip, self.type_med)



