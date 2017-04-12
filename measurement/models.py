from __future__ import unicode_literals

import uuid
from django.contrib.postgres.fields import JSONField
from django.db import models
from event.models import Event, State, Country


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


class Probe(models.Model):

    identification = models.CharField(max_length=50, unique=True)
    region = models.ForeignKey(
        State, related_name='probes', default=3479
    )
    country = models.ForeignKey(
        Country, related_name='probes', default=231
    )
    city = models.CharField(max_length=100)
    isp = models.ForeignKey(ISP)
    plan = models.ForeignKey(
        Plan, null=True, blank=True, related_name='probes')

    def __unicode__(self):
        return u"%s - %s" % (self.identification, self.region)


class DNS(models.Model):

    isp = models.ForeignKey(ISP, verbose_name='Operadora')
    verbose = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    public = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s - %s" % (self.verbose, self.ip)


class Measurement(models.Model):

    _DATABASE = 'titan_db'

    # Test name helper: dns_consistency web_connectivity http_header_field_manipulation http_invalid_request_line
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    input = models.CharField(max_length=50, null=True)
    annotations = JSONField()
    report_id = models.CharField(max_length=100)
    report_filename = models.CharField(max_length=250)
    options = models.TextField(null=True)
    probe_cc = models.CharField(max_length=50)
    probe_asn = models.CharField(max_length=50)
    probe_ip = models.GenericIPAddressField()
    data_format_version = models.CharField(max_length=10)
    test_name = models.CharField(max_length=50)
    test_start_time = models.DateTimeField()
    measurement_start_time = models.DateTimeField()
    test_runtime = models.FloatField()
    test_helpers = models.TextField(null=True)
    test_keys = JSONField()
    software_name = models.CharField(max_length=15)
    software_version = models.CharField(max_length=10)
    test_version = models.CharField(max_length=10)
    bucket_date = models.DateTimeField()

    class Meta:
        db_table = 'metrics'
        managed = False


class Metric(models.Model):

    # Test name helper:
    # dns_consistency
    # web_connectivity
    # http_header_field_manipulation
    # http_invalid_request_line

    measurement = models.CharField(max_length=200)
    input = models.CharField(max_length=50, null=True, db_index=True)
    annotations = JSONField()
    report_id = models.CharField(max_length=100, db_index=True)
    report_filename = models.CharField(max_length=250)
    options = models.TextField(null=True)
    probe_cc = models.CharField(max_length=50)
    probe_asn = models.CharField(max_length=50)
    probe_ip = models.GenericIPAddressField()
    data_format_version = models.CharField(max_length=10)
    test_name = models.CharField(max_length=50, db_index=True)
    test_start_time = models.DateTimeField()
    measurement_start_time = models.DateTimeField(db_index=True)
    test_runtime = models.FloatField()
    test_helpers = models.TextField(null=True)
    test_keys = JSONField()
    software_name = models.CharField(max_length=15)
    software_version = models.CharField(max_length=10)
    test_version = models.CharField(max_length=10, db_index=True)
    bucket_date = models.DateTimeField()
    probe = models.ForeignKey(Probe, null=True, blank=True, db_index=True)

    class Meta:
        index_together = [
            ["test_version", "measurement_start_time"],
        ]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        try:
            probe = self.annotations['probe']
            self.probe = Probe.objects.get(identification=probe)
        except Exception:
            self.probe = None

        return super(Metric, self).save(force_insert=False, force_update=False, using=None,
                                        update_fields=None)


class Flag(models.Model):

    NONE = 'none'
    SOFT = 'soft'
    HARD = 'hard'
    MUTED = 'muted'

    TYPE = {
        NONE: 'None',
        SOFT: 'Soft',
        HARD: 'Hard',
        MUTED: 'Muted',
    }

    TYPE_CHOICES = [    # Items are sorted alphabetically
        (k, v) for k, v in sorted(TYPE.items(), key=lambda t: t[1])]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    metric = models.ForeignKey(Metric, null=True)
    metric_date = models.DateTimeField()

    # ---------------------------------------------------
    flag = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default=NONE, db_index=True)
    manual_flag = models.BooleanField(default=False, db_index=True)
    # ---------------------------------------------------

    event = models.ForeignKey(Event, null=True, blank=True,
                              related_name='flags')
    suggested_events = models.ManyToManyField(
        Event, related_name="suggested_events", blank=True)

    class Meta:
        index_together = [
            ["manual_flag", "flag"],
            ["flag", "manual_flag"],
        ]

    def __unicode__(self):
        return u"%s - %s" % (self.metric_date, self.flag)
