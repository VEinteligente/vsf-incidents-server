from __future__ import unicode_literals

from datetime import datetime, timedelta
from django.db import models
from measurement.models import Probe, Metric, ISP, Flag


class DailyTest(models.Model):

    flag = models.ForeignKey(Flag)
    isp = models.ForeignKey(ISP)
    date = models.DateField()

    ndt_measurement_count = models.PositiveIntegerField(default=0)

    av_upload_speed = models.FloatField(default=0)
    av_download_speed = models.FloatField(default=0)
    av_ping = models.FloatField(default=0)
    av_max_ping = models.FloatField(default=0)
    av_min_ping = models.FloatField(default=0)
    av_timeout = models.FloatField(default=0)
    av_package_loss = models.FloatField(default=0)

    def __unicode__(self):
        return u"%s - %s" % (self.date, self.isp)


class NDTMeasurement(models.Model):

    metric = models.ForeignKey(Metric, related_name='ndt')
    daily_test = models.ForeignKey(DailyTest, null=True, blank=True, related_name='ndt')
    isp = models.ForeignKey(ISP, null=True, blank=True)
    date = models.DateField()

    upload_speed = models.FloatField()
    download_speed = models.FloatField()
    ping = models.FloatField()
    max_ping = models.FloatField()
    min_ping = models.FloatField()
    timeout = models.FloatField()
    package_loss = models.FloatField()
