from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField
from measurement.models import Flag, Metric


class DNS(models.Model):

    flag = models.OneToOneField(Flag, null=True, related_name="dnss")
    metric = models.ForeignKey(Metric, null=True, related_name="dnss")

    control_resolver_failure = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    control_resolver_answers = JSONField(null=True)
    control_resolver_resolver_hostname = models.GenericIPAddressField(
        null=True, blank=True)  # servidor DNS de control

    failure = models.CharField(max_length=50, null=True, blank=True)
    answers = JSONField(null=True)
    resolver_hostname = models.GenericIPAddressField(
        null=True, blank=True)  # servidor DNS que se esta evaluando
