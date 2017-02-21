from __future__ import unicode_literals

from django.db import models
from measurement.models import Probe, Metric


class DayTest(models.Model):

    probe = models.ForeignKey(Probe)
    metric = models.ForeignKey(Metric)
    date = models.DateField()
    week = models.PositiveIntegerField()

    # Average day speed measurement
    day_download = models.FloatField()
    day_upload = models.FloatField()
    day_ping = models.IntegerField()
    day_max_ping = models.IntegerField()
    day_min_ping = models.IntegerField()

    # Average speed for this week
    week_download = models.FloatField()
    week_upload = models.FloatField()
    week_ping = models.IntegerField()
    week_max_ping = models.IntegerField()
    week_min_ping = models.IntegerField()

    # Average speed for this month
    month_download = models.FloatField()
    month_upload = models.FloatField()
    month_ping = models.IntegerField()
    month_max_ping = models.IntegerField()
    month_min_ping = models.IntegerField()

    # Average speed for this year
    year_download = models.FloatField()
    year_upload = models.FloatField()
    year_ping = models.IntegerField()
    year_max_ping = models.IntegerField()
    year_min_ping = models.IntegerField()

    def save(self, *args, **kwargs):
        print("############################")
        print(self.metric.annotations['probe'])
        print(self.metric.test_name)
        print(self.metric.test_start_time)
        print("############################")
        if True:
            return None
        else:
            return super(DayTest, self).save(*args, **kwargs)
