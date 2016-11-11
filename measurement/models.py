from __future__ import unicode_literals

from django.db import models
from event.models import Event


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
    target = models.CharField(max_length=100)
    isp = models.CharField(max_length=100)
    region = models.CharField(max_length=100, default='CCS')
    ip = models.GenericIPAddressField()
    # True -> hard, False -> soft, None -> muted
    flag = models.NullBooleanField(default=False)
    type_med = models.CharField(verbose_name='Tipo de Medicion',
                                max_length=50,
                                choices=TYPE_CHOICES,
                                default=MED)
    event = models.ForeignKey(Event, null=True, blank=True)

    def __unicode__(self):
        return u"%s - %s - %s" % (self.medicion, self.ip, self.type_med)
