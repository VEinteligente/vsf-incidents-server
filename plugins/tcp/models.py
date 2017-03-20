from __future__ import unicode_literals

from django.db import models
from measurement.models import Flag, Metric


class TCP(models.Model):

    flag = models.OneToOneField(Flag, null=True, related_name="tcps")
    metric = models.ForeignKey(Metric, null=True, related_name="tcps")

    status_blocked = models.BooleanField(default=False)
    status_failure = models.TextField(null=True)
    status_success = models.BooleanField(default=True)
