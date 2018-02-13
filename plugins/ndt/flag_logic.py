# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
from datetime import datetime, timedelta

from django.db.models.expressions import RawSQL
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.db.models import Avg, F

from measurement.models import Metric, Flag, ISP, Plan, State, Probe
from models import NDT, DailyTest

SYNCHRONIZE_logger = logging.getLogger('SYNCHRONIZE_logger')


def asignar_isp_y_probes_a_metrics():
    metrics = Metric.objects.filter(test_name='ndt')

    for metric in metrics:
        probe = Probe.objects.order_by('?').first()
        metric.probe = probe
        metric.save()
        try:
            ndt = NDT.objects.get(metric=metric)
            ndt.isp = probe.isp
            ndt.save()
        except NDT.DoesNotExist:
            pass


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
    Translate Metrics with 'ndt' test_name to NDTMeasurement table.
    :return: None
    """

    ndt_metrics_qs = Metric.objects.filter(
        test_name='ndt', ndts=None
    ).select_related('probe').order_by('measurement_start_time')

    sync_date = settings.SYNCHRONIZE_DATE
    if sync_date is not None:
        sync_date = make_aware(parse_datetime(sync_date))

        ndt_metrics_qs = ndt_metrics_qs.filter(bucket_date__gte=sync_date)

    ndt_metrics_count = ndt_metrics_qs.count()
    ndt_metrics_count1 = ndt_metrics_qs.count()

    ndt_metrics_qs = ndt_metrics_qs.annotate(
        download=RawSQL("test_keys->'simple'->'download'", ()),
        upload=RawSQL("test_keys->'simple'->'upload'", ()),
        ping=RawSQL("test_keys->'simple'->'ping'", ()),
        min_ping=RawSQL("test_keys->'advanced'->'min_rtt'", ()),
        max_ping=RawSQL("test_keys->'advanced'->'max_rtt'", ()),
        timeout=RawSQL("test_keys->'advanced'->'timeouts'", ()),
        package_loss=RawSQL("test_keys->'advanced'->'packet_loss'", ()),
    )

    steps = ndt_metrics_count / 1000
    steps = steps + 1 if ndt_metrics_count % 1000 > 0 else steps

    SYNCHRONIZE_logger.info(
        "\nTotal de metrics de NDT: %s - total de paginas %s\n" %
        (ndt_metrics_count1, steps)
    )

    ndt_count = 0
    flags_count = 0
    flags_aborted_count = 0
    errors_count = 0
    num_objects = 0

    failed_ndt_metrics = list()
    for step in range(steps):
        ndt_metrics = ndt_metrics_qs.exclude(id__in=failed_ndt_metrics)
        ndt_metrics_count = ndt_metrics.count()
        SYNCHRONIZE_logger.info(
            "\nPagina %s de NDT, hay %s métricas.\n"
            % (str(step + 1), ndt_metrics_count)
        )

        # The queryset we be covered from tail to head taking batches of
        # 1000 or less (only in the last iteration)
        if ndt_metrics_count < 1000:
            head = 0
        else:
            head = ndt_metrics_count - 1000
        tail = ndt_metrics_count

        metrics = ndt_metrics[head:tail]

        for ndt_metric in metrics:
            num_objects += 1
            flag = Flag(
                metric=ndt_metric,
                metric_date=ndt_metric.bucket_date,
                flag=Flag.NONE,
                manual_flag=False,
                plugin_name=ndt_metric.__class__.__name__
            )
            flag.save()
            flags_count += 1

            isp = None
            if ndt_metric.probe:
                isp = ndt_metric.probe.isp_id

            try:
                ndt = NDT(
                    flag=flag,
                    metric=ndt_metric,
                    isp=isp,
                    date=ndt_metric.bucket_date,
                    upload_speed=ndt_metric.download,
                    download_speed=ndt_metric.upload,
                    ping=ndt_metric.ping,
                    max_ping=ndt_metric.max_ping,
                    min_ping=ndt_metric.min_ping,
                    timeout=ndt_metric.timeout,
                    package_loss=ndt_metric.package_loss
                )
                ndt.save()
                ndt_count += 1
            except Exception as e:
                flags_count -= 1
                flags_aborted_count += 1
                errors_count += 1

                flag.delete()
                failed_ndt_metrics.append(ndt_metric.id)

                SYNCHRONIZE_logger.error(
                    "Fallo en metric_to_ndt, en la metric '%s' con el "
                    "siguiente mensaje: %s"
                    %
                    (str(ndt_metric.measurement), str(e))
                )

    SYNCHRONIZE_logger.error(
        "\n"
        "\nLa 1ra consulta encontró %s métricas para analizar.\n"
        "Se analizaron %s métricas.\n"
        "Sucedieron %s errores.\n"
        "Se crearon %s pruebas NDT.\n"
        "Se crearon %s flags, se abortó la creación de %s flags.\n"
        %
        (
            ndt_metrics_count1, num_objects, errors_count, ndt_count,
            flags_count, flags_aborted_count
        )
    )


def ndt_to_daily_test():
    """
    It takes average of all types of measurements in
    NDTMeasurement and writes them in a DailyTest.
    :return: None
    """
    sync_date = settings.SYNCHRONIZE_DATE
    if sync_date is not None:
        start_date = parse_datetime(sync_date).date()
    else:
        start_date = NDT.objects.all().order_by('date').first().date

    dates = date_range(start_date, datetime.today().date())

    for date in dates:

        isps = NDT.objects.filter(date=date).distinct('isp').values(
            'isp').exclude(isp=None)

        plans = NDT.objects.filter(date=date).annotate(
            plan=F('flag__metric__probe__plan')
        ).distinct('plan').values('plan')

        regions = NDT.objects.filter(date=date).annotate(
            region=F('flag__metric__probe__region')
        ).distinct('region').values('region')

        if isps:
            for isp in isps:
                #############################################################
                # aqui se sacan los daily_test que no tienen ninguna region #
                # y ningun plan o sea, el promedio de todas las metrics por #
                # los isp solamente                                         #
                #############################################################

                ndt_measurements_without_region_and_plan = NDT.objects.filter(
                    date=date,
                    isp=isp['isp']
                )
                avgs = ndt_measurements_without_region_and_plan.aggregate(
                    av_upload_speed=Avg('upload_speed'),
                    av_download_speed=Avg('download_speed'),
                    av_ping=Avg('ping'),
                    av_max_ping=Avg('max_ping'),
                    av_min_ping=Avg('min_ping'),
                    av_timeout=Avg('timeout'),
                    av_package_loss=Avg('package_loss'),
                )

                if avgs['av_upload_speed'] \
                        and avgs['av_download_speed'] \
                        and avgs['av_ping'] \
                        and avgs['av_max_ping'] \
                        and avgs['av_min_ping'] \
                        and avgs['av_timeout'] \
                        and avgs['av_package_loss']:
                    try:
                        try:
                            test = DailyTest.objects.get(
                                date=date,
                                isp=isp['isp'],
                                plan=None,
                                region=None
                            )
                        except DailyTest.DoesNotExist:
                            try:
                                isp_obj = ISP.objects.get(id=isp['isp'])
                                test = DailyTest(isp=isp_obj, date=date)
                                test.save()
                            except (ISP.DoesNotExist, Plan.DoesNotExist) as e:
                                SYNCHRONIZE_logger.exception(
                                    "Fallo en ndt_to_daily_test, en el dia "
                                    "'%s' diciendo que no hay ISP o PLAN: %s"
                                    % (str(date), str(e))
                                )

                        test.av_upload_speed = avgs['av_upload_speed']
                        test.av_download_speed = avgs['av_download_speed']
                        test.av_ping = avgs['av_ping']
                        test.av_max_ping = avgs['av_max_ping']
                        test.av_min_ping = avgs['av_min_ping']
                        test.av_timeout = avgs['av_timeout']
                        test.av_package_loss = avgs['av_package_loss']

                        test.ndt_measurement_count = \
                            ndt_measurements_without_region_and_plan.count()

                        test.save()
                    except Exception as e:
                        SYNCHRONIZE_logger.exception(
                            "Fallo en ndt_to_daily_test, en el dia '%s' con "
                            "el siguiente mensaje: %s" % (str(date), str(e))
                        )

                    ##################################################
                    # Hasta aqui, a partir de aqui se sacan con plan #
                    ##################################################

                #############################################################
                # aqui se sacan los daily_test que no tienen ninguna region #
                # o sea, el promedio de todos los planes de los isp, por    #
                # plan                                                      #
                #############################################################

                for plan in plans:
                    isp_obj = ISP.objects.get(id=isp['isp'])
                    try:
                        plan_obj = Plan.objects.get(
                            id=plan['plan'], isp=isp_obj
                        )
                    except Plan.DoesNotExist:
                        # no existe este plan en este isp
                        # Ej. SuperCable 1Mb en CANTV
                        plan_obj = None

                    if plan_obj:
                        ndt_measurements_without_region = NDT.objects.annotate(
                            plan=F('flag__metric__probe__plan')
                        ).filter(
                            date=date, isp=isp['isp'], plan=plan['plan']
                        )
                        avgs = ndt_measurements_without_region.aggregate(
                            av_upload_speed=Avg('upload_speed'),
                            av_download_speed=Avg('download_speed'),
                            av_ping=Avg('ping'),
                            av_max_ping=Avg('max_ping'),
                            av_min_ping=Avg('min_ping'),
                            av_timeout=Avg('timeout'),
                            av_package_loss=Avg('package_loss'),
                        )

                        if avgs['av_upload_speed'] \
                                and avgs['av_download_speed'] \
                                and avgs['av_ping'] \
                                and avgs['av_max_ping'] \
                                and avgs['av_min_ping'] \
                                and avgs['av_timeout'] \
                                and avgs['av_package_loss']:
                            try:
                                try:
                                    test = DailyTest.objects.get(
                                        date=date,
                                        isp=isp['isp'],
                                        plan=plan['plan'],
                                        region=None
                                    )
                                except DailyTest.DoesNotExist:
                                    try:
                                        test = DailyTest(
                                            isp=isp_obj,
                                            plan=plan_obj,
                                            date=date
                                        )
                                        test.save()
                                    except (
                                        ISP.DoesNotExist, Plan.DoesNotExist
                                    ) as e:
                                        SYNCHRONIZE_logger.exception(
                                            "Fallo en ndt_to_daily_test, en el"
                                            " dia '%s' diciendo que no hay ISP"
                                            " o PLAN: %s" % (
                                                str(date), str(e)
                                            )
                                        )

                                test.av_upload_speed = avgs['av_upload_speed']
                                test.av_download_speed = \
                                    avgs['av_download_speed']
                                test.av_ping = avgs['av_ping']
                                test.av_max_ping = avgs['av_max_ping']
                                test.av_min_ping = avgs['av_min_ping']
                                test.av_timeout = avgs['av_timeout']
                                test.av_package_loss = avgs['av_package_loss']

                                test.ndt_measurement_count = \
                                    ndt_measurements_without_region.count()

                                test.save()
                            except Exception as e:
                                SYNCHRONIZE_logger.exception(
                                    "Fallo en ndt_to_daily_test, en el dia "
                                    "'%s' con el siguiente mensaje: %s" % (
                                        str(date), str(e)
                                    )
                                )

                ####################################################
                # Hasta aqui, a partir de aqui se sacan con region #
                ####################################################

                ##########################################################
                # aqui se sacan los daily_test que no tienen ningun plan #
                # o sea, el promedio de todos los planes de los isp, por #
                # region                                                 #
                ##########################################################

                for region in regions:

                    ndt_measurements_without_plan = NDT.objects.annotate(
                        region=F('flag__metric__probe__region')
                    ).filter(
                        date=date,
                        isp=isp['isp'],
                        region=region['region']
                    )
                    avgs = ndt_measurements_without_plan.aggregate(
                        av_upload_speed=Avg('upload_speed'),
                        av_download_speed=Avg('download_speed'),
                        av_ping=Avg('ping'),
                        av_max_ping=Avg('max_ping'),
                        av_min_ping=Avg('min_ping'),
                        av_timeout=Avg('timeout'),
                        av_package_loss=Avg('package_loss'),
                    )

                    if avgs['av_upload_speed'] \
                            and avgs['av_download_speed'] \
                            and avgs['av_ping'] \
                            and avgs['av_max_ping'] \
                            and avgs['av_min_ping'] \
                            and avgs['av_timeout'] \
                            and avgs['av_package_loss']:
                        try:

                            try:
                                test = DailyTest.objects.get(
                                    date=date,
                                    isp=isp['isp'],
                                    region=region['region'],
                                    plan=None
                                )
                            except DailyTest.DoesNotExist:
                                isp_obj = ISP.objects.get(id=isp['isp'])
                                region_obj = State.objects.get(
                                    id=region['region']
                                )
                                test = DailyTest(
                                    isp=isp_obj,
                                    region=region_obj,
                                    date=date
                                )
                                test.save()

                            test.av_upload_speed = avgs['av_upload_speed']
                            test.av_download_speed = avgs['av_download_speed']
                            test.av_ping = avgs['av_ping']
                            test.av_max_ping = avgs['av_max_ping']
                            test.av_min_ping = avgs['av_min_ping']
                            test.av_timeout = avgs['av_timeout']
                            test.av_package_loss = avgs['av_package_loss']

                            test.ndt_measurement_count =\
                                ndt_measurements_without_plan.count()

                            test.save()
                        except Exception as e:
                            SYNCHRONIZE_logger.exception(
                                "Fallo en ndt_to_daily_test, en el dia '%s' "
                                "con el siguiente mensaje: %s" % (
                                    str(date), str(e)
                                )
                            )

                    ####################################################
                    # Hasta aqui, a partir de aqui se sacan con region #
                    ####################################################

                    ##########################################################
                    # aqui se sacan los daily_test que tienen plan y region  #
                    # o sea, el promedio individual de los dias, por plan de #
                    # isp y region                                           #
                    ##########################################################

                    for plan in plans:

                        ndt_m = NDT.objects.annotate(
                            plan=F('flag__metric__probe__plan'),
                            region=F('flag__metric__probe__region')
                        ).filter(
                            date=date,
                            isp=isp['isp'],
                            plan=plan['plan'],
                            region=region['region']
                        )
                        avgs = ndt_m.aggregate(
                            av_upload_speed=Avg('upload_speed'),
                            av_download_speed=Avg('download_speed'),
                            av_ping=Avg('ping'),
                            av_max_ping=Avg('max_ping'),
                            av_min_ping=Avg('min_ping'),
                            av_timeout=Avg('timeout'),
                            av_package_loss=Avg('package_loss'),
                        )

                        if avgs['av_upload_speed'] \
                                and avgs['av_download_speed'] \
                                and avgs['av_ping'] \
                                and avgs['av_max_ping'] \
                                and avgs['av_min_ping'] \
                                and avgs['av_timeout'] \
                                and avgs['av_package_loss']:
                            try:
                                try:
                                    test = DailyTest.objects.get(
                                        date=date,
                                        isp=isp['isp'],
                                        plan=plan['plan'],
                                        region=region['region']
                                    )
                                except DailyTest.DoesNotExist:
                                    isp_obj = ISP.objects.get(id=isp['isp'])
                                    plan_obj = Plan.objects.get(
                                        id=plan['plan']
                                    )
                                    region_obj = State.objects.get(
                                        id=region['region']
                                    )
                                    test = DailyTest(
                                        isp=isp_obj,
                                        plan=plan_obj,
                                        region=region_obj,
                                        date=date
                                    )
                                    test.save()

                                test.av_upload_speed = avgs['av_upload_speed']
                                test.av_download_speed = \
                                    avgs['av_download_speed']
                                test.av_ping = avgs['av_ping']
                                test.av_max_ping = avgs['av_max_ping']
                                test.av_min_ping = avgs['av_min_ping']
                                test.av_timeout = avgs['av_timeout']
                                test.av_package_loss = avgs['av_package_loss']

                                test.ndt_measurement_count = ndt_m.count()

                                test.save()
                            except Exception as e:
                                SYNCHRONIZE_logger.exception(
                                    "Fallo en ndt_to_daily_test, en el dia "
                                    "'%s' con el siguiente mensaje: %s" % (
                                        str(date), str(e)
                                    )
                                )
