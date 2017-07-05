import logging
from django.db.models.expressions import RawSQL
from django.conf import settings
from django.core.paginator import Paginator
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.db.models import F, Count, Case, When, CharField, Q
from vsf import conf
from measurement.models import Metric, Flag
from event.models import MutedInput, Target
from plugins.http.models import HTTP
from event.utils import suggestedEvents


td_logger = logging.getLogger('TRUE_DEBUG_logger')


def web_connectivity_to_http():
    # Get all metrics with test_name web_connectivity
    # but only values id, measurement, test_keys->'status_code_match',
    # test_keys->'headers_match' and test_keys->'body_length_match'

    td_logger.info("Comenzando con web_connectivity en HTTP")

    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        td_logger.info("Con fecha de inicio para HTTP")
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))
        web_connectivity_metrics = Metric.objects.filter(
            test_name='web_connectivity',
            measurement_start_time__gte=SYNCHRONIZE_DATE
        ).annotate(
            status_code_match=RawSQL(
                "test_keys->'status_code_match'", ()
            ),
            headers_match=RawSQL(
                "test_keys->'headers_match'", ()
            ),
            body_length_match=RawSQL(
                "test_keys->'body_length_match'", ()
            ),
            body_proportion=RawSQL(
                "test_keys->'body_proportion'", ()
            )
        ).values(
            'id',
            'status_code_match',
            'headers_match',
            'body_length_match',
            'body_proportion',
            'input'
        )
    else:
        td_logger.info("Sin fecha de inicio para HTTP")
        web_connectivity_metrics = Metric.objects.filter(
            test_name='web_connectivity'
        ).annotate(
            status_code_match=RawSQL(
                "test_keys->'status_code_match'", ()
            ),
            headers_match=RawSQL(
                "test_keys->'headers_match'", ()
            ),
            body_length_match=RawSQL(
                "test_keys->'body_length_match'", ()
            ),
            body_proportion=RawSQL(
                "test_keys->'body_proportion'", ()
            )
        ).values(
            'id',
            'status_code_match',
            'headers_match',
            'body_length_match',
            'body_proportion',
            'input'
        )

    td_logger.info("Cantidad de metrics para http: %s" % web_connectivity_metrics.count())

    for http_metric in web_connectivity_metrics:
        if (http_metric['status_code_match'] is not None) and (
            http_metric['body_length_match'] is not None) and (
            http_metric['headers_match'] is not None) and (
            http_metric['body_proportion'] is not None
        ):
            http_exist = HTTP.objects.filter(
                metric_id=http_metric['id']
            ).exists()
            if not http_exist:
                url = http_metric['input']
                try:
                    target = Target.objects.get(url=url, type=Target.URL)
                except Target.DoesNotExist:
                    target = Target(url=url, type=Target.URL)
                    target.save()
                except Target.MultipleObjectsReturned:
                    target = Target.objects.filter(url=url, type=Target.URL).first()

                http = HTTP(
                    metric_id=http_metric['id'],
                    status_code_match=http_metric['status_code_match'],
                    headers_match=http_metric['headers_match'],
                    body_length_match=http_metric['body_length_match'],
                    body_proportion=http_metric['body_proportion'],
                    target=target
                )
                http.save()

    td_logger.info("Terminando con web_connectivity en HTTP")


def http_to_flag():
    td_logger.info("Comenzando con http_to_flag")

    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))
        https = HTTP.objects.filter(
            metric__measurement_start_time__gte=SYNCHRONIZE_DATE,
            flag=None
        )
    else:
        https = HTTP.objects.filter(flag=None)

    https = https.select_related('metric', 'flag')

    muteds = MutedInput.objects.filter(
        type_med=MutedInput.DNS
    )

    http_paginator = Paginator(https, 1000)

    for p in http_paginator.page_range:
        page = http_paginator.page(p)

        for http in page.object_list:
            is_flag = False
            if (not http.headers_match) and (
                not http.body_length_match) or (
                not http.status_code_match
            ):
                is_flag = True

            if http.body_proportion <= settings.BODY_PROPORTION_LIMIT:
                is_flag = True

            flag = Flag(
                metric_date=http.metric.measurement_start_time,
                metric=http.metric,
                target=http.target,
                plugin_name=http.__class__.__name__
            )

            # If there is a true flag give 'soft' type
            if is_flag is True:
                flag.flag = Flag.SOFT
                # Check if is a muted input
                muted = muteds.filter(
                    url=http.metric.input
                )
                if muted:
                    flag.flag = Flag.MUTED

            flag.save()
            http.flag = flag
            http.save()

    td_logger.info("terminando con http_to_flag")


def soft_to_hard_flags():
    td_logger.info("Comenzando con soft_to_hard_flags")

    ids = Metric.objects.values_list('id', flat=True)
    second_cond = True
    send_email = False

##########################################################
# Evaluating first condition for hard flags
##########################################################

    ids_cond_1 = list(reversed(ids))[:conf.LAST_REPORTS_Y1]

    ##########################################################
    # Get first all http soft flags
    ##########################################################
    flags = Flag.objects.filter(
        Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
        https__metric__in=ids_cond_1
    ).prefetch_related(
        'https__metric__probe__isp'
    ).annotate(
        isp=Case(
            default=F('https__metric__probe__isp__name'),
            output_field=CharField()
        )

    )

    # Dict than determinate which target/isp has
    # SOFT_FLAG_REPEATED_X1 number of soft flags
    result = flags.values(
        'target',
        'isp'
    ).annotate(
        total_soft=Count(
            Case(
                When(
                    Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
                    then=1
                ),
                output_field=CharField()
            )
        )
    ).filter(total_soft=conf.SOFT_FLAG_REPEATED_X1)

    if result:
        second_cond = False
        for r in result:
            # Get flags to update to hard flags
            flags_to_update_id = flags.filter(
                isp=r['isp'],
                target=r['target']
            ).values_list('id', flat=True)

            flags_to_update = Flag.objects.filter(
                id__in=flags_to_update_id)

            flags_to_update.update(flag=Flag.HARD)

            for flag in flags_to_update:
                suggestedEvents(flag)
                # Here comes the code to suggest events to each hard flag
                # Here comes the code to suggest hard to another
                # hard flags to create a new event

        send_email = True

##########################################################
# Evaluating Second condition for hard flags
# Only if First condition doesnt generate any results
##########################################################
    if second_cond:
        ids_cond_2 = list(reversed(ids))[:conf.LAST_REPORTS_Y2]

    ##########################################################
    # Get first all http soft flags
    ##########################################################
        flags = Flag.objects.filter(
            Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
            https__metric__in=ids_cond_2
        ).prefetch_related(
            'https__metric__probe__region'
        ).annotate(
            isp=Case(
                default=F('https__metric__probe__isp__name'),
                output_field=CharField()
            ),
            region=Case(
                default=F('https__metric__probe__region__name'),
                output_field=CharField()
            )

        )

        # Dict than determinate which target/isp has
        # SOFT_FLAG_REPEATED_X1 number of soft flags
        result = flags.values(
            'target',
            'isp',
            'region'
        ).annotate(
            total_soft=Count(
                Case(
                    When(
                        Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
                        then=1
                    ),
                    output_field=CharField()
                )
            )
        ).filter(total_soft=conf.SOFT_FLAG_REPEATED_X2)

        if result:
            for r in result:
                # Get flags to update to hard flags
                flags_to_update_id = flags.filter(
                    isp=r['isp'],
                    target=r['target'],
                    region=r['region']
                ).values_list('id', flat=True)

                flags_to_update = Flag.objects.filter(
                    id__in=flags_to_update_id)

                flags_to_update.update(flag=Flag.HARD)

                for flag in flags_to_update:
                    suggestedEvents(flag)
                    # Here comes the code to suggest events to each hard flag
                    # Here comes the code to suggest hard to another
                    # hard flags to create a new event

            send_email = True

##########################################################
# Send email to users only if a hard flag was detected
# Only if First condition doesnt generate any results
##########################################################
    if send_email:
        print "Sending email"
        td_logger.info("Sending mails")
        # send_email_users()
    td_logger.info("Terminando con soft_to_hard_flags")


def metric_to_http():
    print "Start Web_connectivity test"
    web_connectivity_to_http()
    print "End Web_connectivity test"
    print "Start HTTP to Flag"
    http_to_flag()
    print "End HTTP to Flag"
    print "Start HARD HTTP Flags"
    soft_to_hard_flags()
    print "End HARD HTTP Flags"
