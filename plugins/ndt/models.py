from __future__ import unicode_literals

from datetime import datetime, timedelta
from django.db import models
from measurement.models import Metric, ISP, Flag, Plan, State


class DailyTest(models.Model):

    isp = models.ForeignKey(ISP)
    region = models.ForeignKey(State, blank=True, null=True)
    plan = models.ForeignKey(Plan, blank=True, null=True)
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


class NDT(models.Model):

    flag = models.OneToOneField(Flag, related_name='ndts')
    metric = models.ForeignKey(Metric, related_name='ndts')
    daily_test = models.ForeignKey(
        DailyTest, null=True, blank=True, related_name='measurement')
    isp = models.ForeignKey(ISP, null=True, blank=True)
    date = models.DateField()

    upload_speed = models.FloatField()
    download_speed = models.FloatField()
    ping = models.FloatField()
    max_ping = models.FloatField()
    min_ping = models.FloatField()
    timeout = models.FloatField()
    package_loss = models.FloatField()

    def __unicode__(self):
        return u"%s" % (
            self.metric.measurement)
