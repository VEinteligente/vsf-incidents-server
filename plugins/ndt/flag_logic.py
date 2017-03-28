from django.db.models.expressions import RawSQL
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

from measurement.models import Metric, Flag
from models import NDTMeasurement, DailyTest


def metric_to_ndt():
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))

        ndt_metrics = Metric.objects.filter(
            test_name='ndt',
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
            time_out=RawSQL(
                "test_keys->'advanced'->'timeouts'", ()
            ),
            package_loss=RawSQL(
                "test_keys->'advanced'->'packet_loss'", ()
            ),
        )
    else:
        ndt_metrics = Metric.objects.filter(
            test_name='ndt'
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
            time_out=RawSQL(
                "test_keys->'advanced'->'timeouts'", ()
            ),
            package_loss=RawSQL(
                "test_keys->'advanced'->'packet_loss'", ()
            ),
        )

    ndt_metrics = ndt_metrics.prefetch_related(
        'dnt'
    ).values(
        'metric',
        'probe',
        'download',
        'upload',
        'ping',
        'max_ping',
        'min_ping',
        'timeout',
        'package_loss',
        'ndt'
    )

    ndt_paginator = Paginator(ndt_metrics, 1000)

    for p in ndt_paginator.page_range:
        page = ndt_paginator.page(p)
        for ndt_metric in page.object_list:
            if ndt_metric['ndt'] is None:
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
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))
        ndts = NDTMeasurement.objects.filter(
            date__gte=SYNCHRONIZE_DATE
        ).order_by('date')
    else:
        ndts = NDTMeasurement.objects.all().order_by('date')

    for ndt in ndts:
        try:
            daily_test = DailyTest.objects.get(date=ndt.date, isp=ndt.isp)
            m_count = daily_test.ndt_measurement_count + 1

            daily_test.av_upload_speed += ndt.upload_speed / m_count
            daily_test.av_download_speed += ndt.download_speed / m_count
            daily_test.av_ping += ndt.ping / m_count
            daily_test.av_max_ping += ndt.max_ping / m_count
            daily_test.av_min_ping += ndt.min_ping / m_count
            daily_test.av_timeout += ndt.timeout / m_count
            daily_test.av_package_loss += ndt.package_loss / m_count

            daily_test.ndt_measurement_count = m_count

            daily_test.save()

        except DailyTest.DoesNotExist:
            Flag(
                metric_date=ndt.date,

                # ---------------------------------------------------
                is_flag=models.BooleanField(default=False, db_index=True),
                # True -> hard, False -> soft, None -> muted
                flag = models.NullBooleanField(default=False, db_index=True),
                manual_flag = models.BooleanField(default=False, db_index=True),
                # ---------------------------------------------------
            )

            DailyTest(
                flag=models.ForeignKey(Flag),
                isp=ndt.isp,
                date=ndt.date,
                ndt_measurement_count=1,
                av_upload_speed=ndt.upload_speed,
                av_download_speed=ndt.download_speed,
                av_ping=ndt.ping,
                av_max_ping=ndt.max_ping,
                av_min_ping=ndt.min_ping,
                av_timeout=ndt.timeout,
                av_package_loss=ndt.package_loss,
            )
