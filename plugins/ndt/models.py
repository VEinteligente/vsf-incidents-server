from __future__ import unicode_literals

from datetime import datetime, timedelta
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
    day_ping = models.FloatField()
    day_max_ping = models.FloatField()
    day_min_ping = models.FloatField()

    # Average speed for this week
    week_download = models.FloatField()
    week_upload = models.FloatField()
    week_ping = models.FloatField()
    week_max_ping = models.FloatField()
    week_min_ping = models.FloatField()

    # Average speed for this month
    month_download = models.FloatField()
    month_upload = models.FloatField()
    month_ping = models.FloatField()
    month_max_ping = models.FloatField()
    month_min_ping = models.FloatField()

    # Average speed for this year
    year_download = models.FloatField()
    year_upload = models.FloatField()
    year_ping = models.FloatField()
    year_max_ping = models.FloatField()
    year_min_ping = models.FloatField()

    def save(self, *args, **kwargs):
        print("############################")
        # print(datetime.date(self.metric.test_start_time).isocalendar()[1])
        print(datetime.now().weekday() + 1)  # ->day number of the week
        print(datetime.now().date().day)  # ->day number of the month
        print(datetime.now().timetuple().tm_yday)  # ->day number of the year
        # print(Metric.objects.filter(
        #     test_name='ndt',
        #     annotations__contains={'probe': str(self.metric.annotations['probe'])},
        #     test_start_time__year=self.metric.test_start_time.year,
        #     test_start_time__month=self.metric.test_start_time.month,
        #     test_start_time__day=self.metric.test_start_time.day - 1
        # ))
        # print(self.metric.annotations['probe'])
        # print(self.metric.test_keys['advanced'])
        print("############################")

        metrics = Metric.objects.filter(
            test_name='ndt',
            annotations__contains={'probe': str(self.probe.identification)},
            test_start_time__year=self.date.year,
            test_start_time__month=self.date.month,
            test_start_time__day=self.date.day
        ).order_by('test_start_time')

        print(self.probe.identification)
        print(metrics)

        # try:
        #     obj = DayTest.objects.get(first_name='John', last_name='Lennon')
        #     obj.save()
        # except DayTest.DoesNotExist:
        #     new_values = {'first_name': 'John', 'last_name': 'Lennon'}
        #     obj = DayTest(**new_values)
        #     obj.save()

        # try:
        #     probe = Probe.objects.get(identification=self.metric.annotations['probe'])
        #     self.probe = probe
        # except Probe.DoesNotExist:
        #     return None
        #
        # self.date = self.metric.test_start_time
        # self.week = datetime.date(self.metric.test_start_time).isocalendar()[1]
        #
        # temp_metric = Metric.objects.filter(
        #     test_name='ndt',
        #     annotations__contains={'probe': str(self.metric.annotations['probe'])},
        #     test_start_time__year=self.date.year,
        #     test_start_time__month=self.date.month,
        #     test_start_time__day=self.date.day
        # )
        #
        # i = 0
        # download = 0
        # upload = 0
        # ping = 0
        # for temp in temp_metric:
        #
        #     try:
        #         if self.day_max_ping < self.metric.test_keys['advanced']['max_rtt']:
        #             self.day_max_ping = self.metric.test_keys['advanced']['max_rtt']
        #     except TypeError:
        #         print('shit')
        #         self.day_min_ping = self.metric.test_keys['advanced']['min_rtt']
        #
        #     if temp.test_keys['simple']:
        #         download += temp.test_keys['simple']['download']
        #         upload += temp.test_keys['simple']['upload']
        #         ping += temp.test_keys['simple']['ping']
        #         i += 1
        #
        # download = download/i
        # upload = upload/i
        # ping = ping/i
        #
        # self.day_download = download
        # self.day_upload = upload
        # self.day_ping = ping
        #
        # try:
        #     yesterday = self.date - timedelta(days=1)
        #     print(yesterday)
        #     yesterday = DayTest.objects.get(date=yesterday)
        # except DayTest.DoesNotExist:
        #     print('stuff')
        #
        # #  week logic
        #
        # try:
        #     test_day = DayTest.objects.get(date=self.metric.test_start_time)
        #
        #     if test_day.day_max_ping < self.day_max_ping:
        #         test_day.day_max_ping = self.day_max_ping
        #     if test_day.day_min_ping > self.day_min_ping:
        #         test_day.day_min_ping = self.day_min_ping
        #
        # except DayTest.DoesNotExist:
        #     print(download, ' ', upload, ' ', ping, ' ', i)

        if True:
            return None
        else:
            return super(DayTest, self).save(*args, **kwargs)
