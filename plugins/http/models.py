from __future__ import unicode_literals

from django.db import models
from measurement.models import Flag, Metric


class HTTP(models.Model):

    flag = models.OneToOneField(Flag, null=True)
    metric = models.ForeignKey(Metric, null=True)

    status_code_match = models.BooleanField(default=False)
    headers_match = models.BooleanField(default=False)
    body_length_match = models.BooleanField(default=False)
