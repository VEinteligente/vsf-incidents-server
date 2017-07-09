from __future__ import unicode_literals

import uuid
from django.contrib.postgres.fields import JSONField
from django.db import models
from event.models import Event, State, Country, ISP, Plan, Target


class Probe(models.Model):

    identification = models.CharField(max_length=50, unique=True)
    region = models.ForeignKey(
        State, related_name='probes', default=3479,
        null=True, blank=True
    )
    country = models.ForeignKey(
        Country, related_name='probes', default=231,
        null=True, blank=True
    )
    city = models.CharField(max_length=100, null=True, blank=True)
    isp = models.ForeignKey(ISP, null=True, blank=True)
    plan = models.ForeignKey(
        Plan, null=True, blank=True, related_name='probes'
    )

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

    measurement = models.CharField(max_length=200, unique=True)
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
    probe = models.ForeignKey(
        Probe, null=True, blank=True, db_index=True)

    class Meta:
        index_together = [
            ["test_version", "measurement_start_time"],
        ]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        try:
            probe = self.annotations['probe']
        except Exception:
            try:
                p = Probe.objects.get(identification='no_id')
            except Probe.DoesNotExist:
                p = Probe(identification='no_id')
                p.save()
            self.probe = p
            return super(Metric, self).save(force_insert=False,
                                            force_update=False,
                                            using=None,
                                            update_fields=None)

        try:
            self.probe = Probe.objects.get(identification=probe)
        except Exception:
            p = Probe(identification=probe)
            p.save()
            self.probe = p

        return super(Metric, self).save(force_insert=False, force_update=False, using=None,
                                        update_fields=None)

    def __unicode__(self):

        return u"%s -> %s" % (self.test_name, self.measurement)


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
    target = models.ForeignKey(Target, null=True, blank=True)
    plugin_name = models.CharField(max_length=100, null=True, blank=True)

    # ---------------------------------------------------
    flag = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default=NONE, db_index=True)
    manual_flag = models.BooleanField(default=False, db_index=True)
    # ---------------------------------------------------

    event = models.ForeignKey(Event, null=True, blank=True,
                              related_name='flags')
    suggested_events = models.ManyToManyField(
        Event, related_name="suggested_flags", blank=True)

    class Meta:
        index_together = [
            ["manual_flag", "flag"],
            ["flag", "manual_flag"],
        ]

    def __unicode__(self):
        return u"%s - %s" % (self.metric_date, self.flag)
