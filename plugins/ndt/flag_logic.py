from datetime import datetime, timedelta

from django.db.models.expressions import RawSQL
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.db.models import Avg

from measurement.models import Metric, Flag, ISP
from models import NDTMeasurement, DailyTest


def date_range(start_date, end_date):
    """
    Auxiliary function that helps to take the rank
    between two dates.
    :param start_date: Date range start.
    :param end_date: Date range end.
    :return: date type
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def metric_to_ndt():
    """
    Translate Metrics with 'ndt' test_name to
    NDTMeasurement table.
    :return: None
    """
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))

        ndt_metrics = Metric.objects.filter(
            test_name='ndt',
            ndt=None,
            measurement_start_time__gte=SYNCHRONIZE_DATE
        ).annotate(
            download=RawSQL(
                "test_keys->'simple'->'download'", ()
            ),
            upload=RawSQL(
                "test_keys->'simple'->'upload'", ()
            ),
            ping=RawSQL(
                "test_keys->'simple'->'ping'", ()
            ),
            min_ping=RawSQL(
                "test_keys->'advanced'->'min_rtt'", ()
            ),
            max_ping=RawSQL(
                "test_keys->'advanced'->'max_rtt'", ()
            ),
            timeout=RawSQL(
                "test_keys->'advanced'->'timeouts'", ()
            ),
            package_loss=RawSQL(
                "test_keys->'advanced'->'packet_loss'", ()
            ),
        )
    else:
        ndt_metrics = Metric.objects.filter(
            test_name='ndt',
            ndt=None,
        ).annotate(
            download=RawSQL(
                "test_keys->'simple'->'download'", ()
            ),
            upload=RawSQL(
                "test_keys->'simple'->'upload'", ()
            ),
            ping=RawSQL(
                "test_keys->'simple'->'ping'", ()
            ),
            min_ping=RawSQL(
                "test_keys->'advanced'->'min_rtt'", ()
            ),
            max_ping=RawSQL(
                "test_keys->'advanced'->'max_rtt'", ()
            ),
            timeout=RawSQL(
                "test_keys->'advanced'->'timeouts'", ()
            ),
            package_loss=RawSQL(
                "test_keys->'advanced'->'packet_loss'", ()
            ),
        )

    ndt_metrics = ndt_metrics.prefetch_related(
        'ndt'
    )

    ndt_paginator = Paginator(ndt_metrics, 1000)

    for p in ndt_paginator.page_range:
        page = ndt_paginator.page(p)
        for ndt_metric in page.object_list:
            if ndt_metric.probe is None:
                isp = None
            else:
                isp = ndt_metric.probe.isp
            ndt = NDTMeasurement(
                metric=ndt_metric,
                isp=isp,
                date=ndt_metric.measurement_start_time,
                upload_speed=ndt_metric.download,
                download_speed=ndt_metric.upload,
                ping=ndt_metric.ping,
                max_ping=ndt_metric.max_ping,
                min_ping=ndt_metric.min_ping,
                timeout=ndt_metric.timeout,
                package_loss=ndt_metric.package_loss
            )
            ndt.save()


def ndt_to_daily_test():
    """
    It takes average of all types of measurements in
    NDTMeasurement and writes them in a DailyTest.
    :return: None
    """
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        start_date = make_aware(parse_datetime(SYNCHRONIZE_DATE).date())
    else:
        start_date = NDTMeasurement.objects.all().order_by('date').first().date

    for date in date_range(start_date, datetime.today().date()):

        isps = NDTMeasurement.objects.filter(date=date).distinct('isp').values('isp')

        for isp in isps:
            ndt_m = NDTMeasurement.objects.filter(date=date, isp=isp['isp'])
            averages = ndt_m.aggregate(
                av_upload_speed=Avg('upload_speed'),
                av_download_speed=Avg('download_speed'),
                av_ping=Avg('ping'),
                av_max_ping=Avg('max_ping'),
                av_min_ping=Avg('min_ping'),
                av_timeout=Avg('timeout'),
                av_package_loss=Avg('package_loss'),
            )

            try:
                daily_test = DailyTest.objects.get(date=date, isp=isp['isp'])
            except DailyTest.DoesNotExist:
                flag = Flag(
                    metric_date=date,
                    flag=Flag.NONE,
                    manual_flag=False
                )
                flag.save()
                isp_obj = ISP.objects.get(id=isp['isp'])
                daily_test = DailyTest(
                    flag=flag,
                    isp=isp_obj,
                    date=date
                )
                daily_test.save()

            daily_test.av_upload_speed = averages['av_upload_speed']
            daily_test.av_download_speed = averages['av_download_speed']
            daily_test.av_ping = averages['av_ping']
            daily_test.av_max_ping = averages['av_max_ping']
            daily_test.av_min_ping = averages['av_min_ping']
            daily_test.av_timeout = averages['av_timeout']
            daily_test.av_package_loss = averages['av_package_loss']

            daily_test.ndt_measurement_count = ndt_m.count()

            daily_test.save()
