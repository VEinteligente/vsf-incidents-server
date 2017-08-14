import logging
from urlparse import urlparse
from django.db.models.expressions import RawSQL
from django.conf import settings
from django.core.paginator import Paginator
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.db.models import F, Count, Case, When, CharField, Q
from vsf import conf
from measurement.models import Metric, Flag
from event.models import MutedInput, Target
from plugins.tcp.models import TCP
from event.utils import suggestedEvents

td_logger = logging.getLogger('TRUE_DEBUG_logger')
SYNCHRONIZE_logger = logging.getLogger('SYNCHRONIZE_logger')

def web_connectivity_to_tcp():
    # Get all metrics with test_name web_connectivity
    # but only values id, measurement, test_keys->'status_code_match',
    # test_keys->'headers_match' and test_keys->'body_length_match'
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))
        web_connectivity_metrics = Metric.objects.filter(
            test_name='web_connectivity',
            measurement_start_time__gte=SYNCHRONIZE_DATE
        ).annotate(
            tcp_connect=RawSQL(
                "test_keys->'tcp_connect'", ()
            )
        )
    else:
        web_connectivity_metrics = Metric.objects.filter(
            test_name='web_connectivity'
        ).annotate(
            tcp_connect=RawSQL(
                "test_keys->'tcp_connect'", ()
            )
        )

    web_connectivity_metrics = web_connectivity_metrics.prefetch_related(
        'tcps'
    ).values(
        'id',
        'tcp_connect',
        'tcps',
        'input'
    )

    web_connectivity_paginator = Paginator(web_connectivity_metrics, 1000)

    for p in web_connectivity_paginator.page_range:
        page = web_connectivity_paginator.page(p)
        SYNCHRONIZE_logger.info(
            "Page %i of %s" % (p, str(web_connectivity_paginator.page_range)))
        for tcp_metric in page.object_list:
            for tcp_connect in tcp_metric['tcp_connect']:
                try:
                    if tcp_metric['tcps'] is None and (
                        tcp_connect['status']['blocked'] is not None) and (
                        tcp_connect['status']['success'] is not None
                    ):
                        parsed_uri = urlparse(tcp_metric['input'])
                        current_domain=parsed_uri.netloc

                        try:
                            target = Target.objects.get(
                                ip=tcp_connect['ip'],
                                type=Target.IP,
                                domain=current_domain
                            )
                        except Target.DoesNotExist:
                            try: 
                                current_domain
                            except NameError:
                                target.save()
                                target = Target(
                                    ip=tcp_connect['ip'],
                                    type=Target.IP,
                                )
                                target.save()
                                td_logger.error("IP Target created %s - without domain" % (tcp_connect['ip']))                            
#                                 td_logger.error("IP Target created  - without domain")                            
                            else:
                                target = Target(
                                    ip=tcp_connect['ip'],
                                    type=Target.IP,
                                    domain=current_domain
                                )
                                target.save()
#                                 td_logger.debug("IP Target created  - domain %s" % ( current_domain))                            
                                td_logger.debug("IP Target created %s - domain %s" % (tcp_connect['ip'], current_domain))                            
                                
                        except Target.MultipleObjectsReturned:
                            target = Target.objects.filter(
                                ip=tcp_connect['ip'],
                                type=Target.IP,
                                domain=current_domain
                            ).first()
                            
                        #  for logging only                       
                                                        
                        tcp = TCP(
                            metric_id=tcp_metric['id'],
                            status_blocked=tcp_connect['status']['blocked'],
                            status_failure=tcp_connect['status']['failure'],
                            status_success=tcp_connect['status']['success'],
                            target=target
                        )
                        tcp.save()
                except Exception as e:
                    SYNCHRONIZE_logger.exception("Fallo en web_connectivity_to_tcp, en la metric '%s' con el "
                                             "siguiente mensaje: %s" % (str(tcp_metric['id']), str(e)))


def tcp_to_flag():

    tcp = TCP.objects.filter(flag=None)

    tcp_paginator = Paginator(tcp, 1000)

    muteds = MutedInput.objects.filter(
        type_med=MutedInput.TCP
    )

    for p in tcp_paginator.page_range:
        print tcp_paginator.count
        page = tcp_paginator.page(p)
        SYNCHRONIZE_logger.info(
            "Page %i of %s" % (p, str(tcp_paginator.page_range)))

        for tcp_obj in page.object_list:
            try:
                flag = Flag(
                    metric_date=tcp_obj.metric.measurement_start_time,
                    metric=tcp_obj.metric,
                    target=tcp_obj.target,
                    isp=tcp_obj.metric.probe.isp,
                    plugin_name=tcp_obj.__class__.__name__
                )
                # If there is a true flag give 'soft' type
                if tcp_obj.status_blocked is True:
                    flag.flag = Flag.SOFT
                    # Check if is a muted input
                    muted = muteds.filter(
                        url=tcp_obj.metric.input
                    )
                    if muted:
                        flag.flag = Flag.MUTED
                flag.save()
                tcp_obj.flag = flag
                tcp_obj.save()
            except Exception as e:
                SYNCHRONIZE_logger.exception("Fallo en tcp_to_flag, en el TCP '%s' con el "
                                         "siguiente mensaje: %s" % (str(tcp_obj.id), str(e)))


def soft_to_hard_flags():
    ids = Metric.objects.values_list('id', flat=True)
    second_cond = True
    send_email = False

##########################################################
# Evaluating first condition for hard flags
##########################################################

    ids_cond_1 = list(reversed(ids))[:conf.LAST_REPORTS_Y1]

    ##########################################################
    # Get first all tcp soft flags
    ##########################################################
    flags = Flag.objects.filter(
        Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
        tcps__metric__in=ids_cond_1
    ).prefetch_related(
        'tcps__metric__probe__isp'
    ).annotate(
        isp=Case(
            default=F('tcps__metric__probe__isp__name'),
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
    # Get first all tcp soft flags
    ##########################################################
        flags = Flag.objects.filter(
            Q(flag=Flag.SOFT) | Q(flag=Flag.HARD),
            tcps__metric__in=ids_cond_2
        ).prefetch_related(
            'tcps__metric__probe__region'
        ).annotate(
            isp=Case(
                default=F('tcps__metric__probe__isp__name'),
                output_field=CharField()
            ),
            region=Case(
                default=F('tcps__metric__probe__region__name'),
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
        # send_email_users()


def both():
    web_connectivity_to_tcp()
    tcp_to_flag()


def metric_to_tcp():
    print "Start Web_connectivity test"
    web_connectivity_to_tcp()
    print "End Web_connectivity test"
    print "Start TCP to Flag"
    tcp_to_flag()
    print "End TCP to Flag"
    print "Start HARD TCP Flags"
    soft_to_hard_flags()
    print "End HARD TCP Flags"


def test():
    t = TCP.objects.all()

    for i in t:
        print i.flag.is_flag
