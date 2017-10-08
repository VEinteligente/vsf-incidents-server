import logging
from datetime import datetime, timedelta

from django.db.models.expressions import RawSQL
from django.core.paginator import Paginator
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
    Translate Metrics with 'ndt' test_name to
    NDTMeasurement table.
    :return: None
    """
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))

        ndt_metrics = Metric.objects.filter(
            test_name='ndt',
            ndts=None,
            bucket_date__gte=SYNCHRONIZE_DATE
        )
    else:
        ndt_metrics = Metric.objects.filter(
            test_name='ndt',
            ndts=None,
        )

    ndt_metrics = ndt_metrics.annotate(
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

    ndt_paginator = Paginator(ndt_metrics, 1000)
    SYNCHRONIZE_logger.info("Aqui el total de metrics de NDT: %s - total de paginas de 1000 metrics: %s" %
                            (str(ndt_metrics.count()), str(ndt_paginator.page_range)))

    for p in ndt_paginator.page_range:
        SYNCHRONIZE_logger.info("Pagina %s de NDT" % str(p))
        page = ndt_paginator.page(p)
        for ndt_metric in page.object_list:
            try:
                if ndt_metric.probe is None:
                    isp = None
                else:
                    isp = ndt_metric.probe.isp
                flag = Flag(
                    metric=ndt_metric,
                    metric_date=ndt_metric.bucket_date,
                    flag=Flag.NONE,
                    manual_flag=False,
                    plugin_name=ndt_metric.__class__.__name__
                )
                flag.save()
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
            except Exception as e:
                SYNCHRONIZE_logger.error("Fallo en metric_to_ndt, en la metric '%s' con el "
                                         "siguiente mensaje: %s" % (str(ndt_metric.measurement), str(e)))


def ndt_to_daily_test():
    """
    It takes average of all types of measurements in
    NDTMeasurement and writes them in a DailyTest.
    :return: None
    """
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        start_date = parse_datetime(SYNCHRONIZE_DATE).date()
    else:
        start_date = NDT.objects.all().order_by('date').first().date

    for date in date_range(start_date, datetime.today().date()):

        isps = NDT.objects.filter(date=date).distinct('isp').values('isp').exclude(isp=None)
        plans = NDT.objects.filter(
            date=date
        ).annotate(
            plan=F('flag__metric__probe__plan')
        ).distinct(
            'plan'
        ).values(
            'plan'
        )
        regions = NDT.objects.filter(
            date=date
        ).annotate(
            region=F('flag__metric__probe__region')
        ).distinct(
            'region'
        ).values(
            'region'
        )

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
                averages = ndt_measurements_without_region_and_plan.aggregate(
                    av_upload_speed=Avg('upload_speed'),
                    av_download_speed=Avg('download_speed'),
                    av_ping=Avg('ping'),
                    av_max_ping=Avg('max_ping'),
                    av_min_ping=Avg('min_ping'),
                    av_timeout=Avg('timeout'),
                    av_package_loss=Avg('package_loss'),
                )

                if averages['av_upload_speed'] \
                        and averages['av_download_speed'] \
                        and averages['av_ping'] \
                        and averages['av_max_ping'] \
                        and averages['av_min_ping'] \
                        and averages['av_timeout'] \
                        and averages['av_package_loss']:
                    try:
                        try:
                            daily_test = DailyTest.objects.get(
                                date=date,
                                isp=isp['isp'],
                                plan=None,
                                region=None
                            )
                        except DailyTest.DoesNotExist:
                            try:
                                isp_obj = ISP.objects.get(id=isp['isp'])
                                daily_test = DailyTest(
                                    isp=isp_obj,
                                    date=date
                                )
                                daily_test.save()
                            except (ISP.DoesNotExist, Plan.DoesNotExist) as e:
                                SYNCHRONIZE_logger.exception("Fallo en ndt_to_daily_test, en el dia '%s' diciendo "
                                                             "q no hay ISP o PLAN: %s" % (str(date), str(e)))

                        daily_test.av_upload_speed = averages['av_upload_speed']
                        daily_test.av_download_speed = averages['av_download_speed']
                        daily_test.av_ping = averages['av_ping']
                        daily_test.av_max_ping = averages['av_max_ping']
                        daily_test.av_min_ping = averages['av_min_ping']
                        daily_test.av_timeout = averages['av_timeout']
                        daily_test.av_package_loss = averages['av_package_loss']

                        daily_test.ndt_measurement_count = ndt_measurements_without_region_and_plan.count()

                        daily_test.save()
                    except Exception as e:
                        SYNCHRONIZE_logger.exception("Fallo en ndt_to_daily_test, en el dia '%s' con el "
                                                     "siguiente mensaje: %s" % (str(date), str(e)))

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
                        plan_obj = Plan.objects.get(id=plan['plan'], isp=isp_obj)
                    except Plan.DoesNotExist:
                        # no existe este plan en este isp
                        # Ej. SuperCable 1Mb en CANTV
                        plan_obj = None

                    if plan_obj:

                        ndt_measurements_without_region = NDT.objects.annotate(
                            plan=F('flag__metric__probe__plan')
                        ).filter(
                            date=date,
                            isp=isp['isp'],
                            plan=plan['plan']
                        )
                        averages = ndt_measurements_without_region.aggregate(
                            av_upload_speed=Avg('upload_speed'),
                            av_download_speed=Avg('download_speed'),
                            av_ping=Avg('ping'),
                            av_max_ping=Avg('max_ping'),
                            av_min_ping=Avg('min_ping'),
                            av_timeout=Avg('timeout'),
                            av_package_loss=Avg('package_loss'),
                        )

                        if averages['av_upload_speed'] \
                                and averages['av_download_speed'] \
                                and averages['av_ping'] \
                                and averages['av_max_ping'] \
                                and averages['av_min_ping'] \
                                and averages['av_timeout'] \
                                and averages['av_package_loss']:
                            try:
                                try:
                                    daily_test = DailyTest.objects.get(
                                        date=date,
                                        isp=isp['isp'],
                                        plan=plan['plan'],
                                        region=None
                                    )
                                except DailyTest.DoesNotExist:
                                    try:
                                        daily_test = DailyTest(
                                            isp=isp_obj,
                                            plan=plan_obj,
                                            date=date
                                        )
                                        daily_test.save()
                                    except (ISP.DoesNotExist, Plan.DoesNotExist) as e:
                                        SYNCHRONIZE_logger.exception("Fallo en ndt_to_daily_test, en el dia '%s' diciendo "
                                                                     "q no hay ISP o PLAN: %s" % (str(date), str(e)))

                                daily_test.av_upload_speed = averages['av_upload_speed']
                                daily_test.av_download_speed = averages['av_download_speed']
                                daily_test.av_ping = averages['av_ping']
                                daily_test.av_max_ping = averages['av_max_ping']
                                daily_test.av_min_ping = averages['av_min_ping']
                                daily_test.av_timeout = averages['av_timeout']
                                daily_test.av_package_loss = averages['av_package_loss']

                                daily_test.ndt_measurement_count = ndt_measurements_without_region.count()

                                daily_test.save()
                            except Exception as e:
                                SYNCHRONIZE_logger.exception("Fallo en ndt_to_daily_test, en el dia '%s' con el "
                                                             "siguiente mensaje: %s" % (str(date), str(e)))

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
                    averages = ndt_measurements_without_plan.aggregate(
                        av_upload_speed=Avg('upload_speed'),
                        av_download_speed=Avg('download_speed'),
                        av_ping=Avg('ping'),
                        av_max_ping=Avg('max_ping'),
                        av_min_ping=Avg('min_ping'),
                        av_timeout=Avg('timeout'),
                        av_package_loss=Avg('package_loss'),
                    )

                    if averages['av_upload_speed'] \
                            and averages['av_download_speed'] \
                            and averages['av_ping'] \
                            and averages['av_max_ping'] \
                            and averages['av_min_ping'] \
                            and averages['av_timeout'] \
                            and averages['av_package_loss']:
                        try:

                            try:
                                daily_test = DailyTest.objects.get(
                                    date=date,
                                    isp=isp['isp'],
                                    region=region['region'],
                                    plan=None
                                )
                            except DailyTest.DoesNotExist:
                                isp_obj = ISP.objects.get(id=isp['isp'])
                                region_obj = State.objects.get(id=region['region'])
                                daily_test = DailyTest(
                                    isp=isp_obj,
                                    region=region_obj,
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

                            daily_test.ndt_measurement_count = ndt_measurements_without_plan.count()

                            daily_test.save()
                        except Exception as e:
                            SYNCHRONIZE_logger.exception("Fallo en ndt_to_daily_test, en el dia '%s' con el "
                                                         "siguiente mensaje: %s" % (str(date), str(e)))

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
                        averages = ndt_m.aggregate(
                            av_upload_speed=Avg('upload_speed'),
                            av_download_speed=Avg('download_speed'),
                            av_ping=Avg('ping'),
                            av_max_ping=Avg('max_ping'),
                            av_min_ping=Avg('min_ping'),
                            av_timeout=Avg('timeout'),
                            av_package_loss=Avg('package_loss'),
                        )

                        if averages['av_upload_speed'] \
                                and averages['av_download_speed'] \
                                and averages['av_ping'] \
                                and averages['av_max_ping'] \
                                and averages['av_min_ping'] \
                                and averages['av_timeout'] \
                                and averages['av_package_loss']:
                            try:
                                try:
                                    daily_test = DailyTest.objects.get(
                                        date=date,
                                        isp=isp['isp'],
                                        plan=plan['plan'],
                                        region=region['region']
                                    )
                                except DailyTest.DoesNotExist:
                                    isp_obj = ISP.objects.get(id=isp['isp'])
                                    plan_obj = Plan.objects.get(id=plan['plan'])
                                    region_obj = State.objects.get(id=region['region'])
                                    daily_test = DailyTest(
                                        isp=isp_obj,
                                        plan=plan_obj,
                                        region=region_obj,
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
                            except Exception as e:
                                SYNCHRONIZE_logger.exception("Fallo en ndt_to_daily_test, en el dia '%s' con el "
                                                             "siguiente mensaje: %s" % (str(date), str(e)))
