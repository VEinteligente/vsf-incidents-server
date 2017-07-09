from __future__ import unicode_literals

from django.db import models
from event.models import Target
from measurement.models import Flag, Metric


class HTTP(models.Model):

    flag = models.OneToOneField(Flag, null=True, related_name="https")
    metric = models.ForeignKey(Metric, null=True, related_name="https")

    status_code_match = models.BooleanField(default=False)
    headers_match = models.BooleanField(default=False)
    body_length_match = models.BooleanField(default=False)

    body_proportion = models.FloatField()
    target = models.ForeignKey(Target, null=True, blank=True)

    def __unicode__(self):
        return u"%s - %s - Flag: %s" % (
            self.metric.input, self.metric.measurement, self.flag.flag)
