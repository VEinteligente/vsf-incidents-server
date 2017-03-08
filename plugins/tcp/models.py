from __future__ import unicode_literals

from django.db import models
from measurement.models import Flag, Metric


class TCP(models.Model):

    flag = models.OneToOneField(Flag)
    metric = models.ForeignKey(Metric)

    status_blocked = models.BooleanField(default=False)
    status_failure = models.TextField()
    status_success = models.BooleanField(default=True)
