from django.db.models.expressions import RawSQL
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

from measurement.models import Metric, Flag
from plugins.dns.models import DNS


def web_connectivity_to_dns():
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))

        web_connectivity_metrics = Metric.objects.filter(
            test_name='web_connectivity',
            measurement_start_time__gte=SYNCHRONIZE_DATE
        ).annotate(
            queries=RawSQL(
                "test_keys->'queries'", ()
            ),
            control_resolver=RawSQL(
                "test_keys->'control'->'dns'", ()
            )
        )
    else:
        web_connectivity_metrics = Metric.objects.filter(
            test_name='web_connectivity'
        ).annotate(
            queries=RawSQL(
                "test_keys->'queries'", ()
            ),
            control_resolver=RawSQL(
                "test_keys->'control'", ()
            )
        )

    web_connectivity_metrics = web_connectivity_metrics.prefetch_related(
        'dnss'
    ).values(
        'id',
        'measurement',
        'queries',
        'control_resolver',
        'dnss'
    )

    dns_paginator = Paginator(web_connectivity_metrics, 1000)

    for p in dns_paginator.page_range:
        page = dns_paginator.page(p)
        for dns_metric in page.object_list:
            cr = {}
            try:
                cr['failure'] = dns_metric['control_resolver']['dns']['failure']
            except Exception:
                cr['failure'] = None

            try: 
                cr['answers'] = {'addrs': dns_metric['control_resolver']['dns']['addrs']}
            except Exception:
                cr['answers'] = None

            for query in dns_metric['queries']:
                for answer in query['answers']:
                    if dns_metric['dnss'] is None:
                        dns = DNS(
                            metric_id=dns_metric['id'],
                            control_resolver_failure=cr['failure'],
                            control_resolver_answers=cr['answers'],
                            failure=query['failure'],
                            answers=answer
                        )
                        dns.save()


def dns_consistency_to_dns():
    # Get all metrics with test_name dns_consistency
    # but only values measurement, test_keys->'queries'
    # and test_keys->'control_resolver'
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))

        dns_consistency_metrics = Metric.objects.filter(
            test_name='dns_consistency',
            measurement_start_time__gte=SYNCHRONIZE_DATE
        ).annotate(
            queries=RawSQL(
                "test_keys->'queries'", ()
            ),
            control_resolver=RawSQL(
                "test_keys->'control_resolver'", ()
            )
        )
    else:
        dns_consistency_metrics = Metric.objects.filter(
            test_name='dns_consistency'
        ).annotate(
            queries=RawSQL(
                "test_keys->'queries'", ()
            ),
            control_resolver=RawSQL(
                "test_keys->'control_resolver'", ()
            )
        )

    dns_consistency_metrics = dns_consistency_metrics.prefetch_related(
        'dnss'
    ).values(
        'id',
        'measurement',
        'queries',
        'control_resolver',
        'dnss'
    )

    # for each dns metric get control resolver and other fields

    for dns_metric in dns_consistency_metrics:
        # Get control_resolver ip address
        cr_ip = dns_metric['control_resolver'].split(':')[0]

        # Get control_resolver
        cr = {}
        for query in dns_metric['queries']:
            # searching for control resolver
            if query['resolver_hostname'] == cr_ip:
                cr['failure'] = query['failure']
                cr['answers'] = query['answers']
                cr['resolver_hostname'] = query['resolver_hostname']

        for query in dns_metric['queries']:
            if query['resolver_hostname'] != cr_ip:
                if dns_metric['dnss'] is None:
                    dns = DNS(
                        metric_id=dns_metric['id'],
                        control_resolver_failure=cr['failure'],
                        control_resolver_answers=cr['answers'],
                        control_resolver_resolver_hostname=cr['resolver_hostname'],
                        failure=query['failure'],
                        answers=query['answers'],
                        resolver_hostname=query['resolver_hostname'],
                    )
                    dns.save()


def dns_to_flag():
    SYNCHRONIZE_DATE = settings.SYNCHRONIZE_DATE
    if SYNCHRONIZE_DATE is not None:
        SYNCHRONIZE_DATE = make_aware(parse_datetime(settings.SYNCHRONIZE_DATE))
        dnss = DNS.objects.filter(
            metric__measurement_start_time__gte=SYNCHRONIZE_DATE
        )
    else:
        dnss = DNS.objects.all()

    dnss = dnss.select_related('metric', 'flag')

    print dnss.count()
    dns_paginator = Paginator(dnss, 1000)
    print dns_paginator.page_range

    for p in dns_paginator.page_range:
        page = dns_paginator.page(p)

        for dns in page.object_list:
            is_flag = False
            if dns.metric.test_name == 'dns_consistency':
                if dns.control_resolver_failure is None:
                    if dns.failure == "no_answer":
                        is_flag = True
                    else:
                        if dns.failure is None:
                            if dns.control_resolver_answers != dns.answers:
                                is_flag = True

            if dns.metric.test_name == 'web_connectivity':
                if (dns.control_resolver_failure is None) and (
                    dns.control_resolver_answers is not None
                ):
                    if dns.failure == "no_answer":
                        is_flag = True
                    else:
                        if dns.failure is None and dns.answers is not None:
                            try:
                                addr = dns.answers['ipv4']
                            except Exception:
                                try:
                                    addr = dns.answers['ipv6']
                                except Exception:
                                    addr = dns.answers['hostname']
                            if addr not in dns.control_resolver_answers['addrs']:
                                is_flag = True

            if dns.flag is not None:
                if dns.flag.is_flag != is_flag:
                    dns.flag.is_flag = is_flag
                    dns.flag.save()
            else:
                print "Debi entrar aqui"
                flag = Flag(
                    is_flag=is_flag,
                    metric_date=dns.metric.measurement_start_time
                )
                flag.save()
                dns.flag = flag
                dns.save()

        print page


def metric_to_dns():
    print "Start Web_connectivity test"
    web_connectivity_to_dns()
    print "End Web_connectivity test"
    print "Start dns_consistency test"
    dns_consistency_to_dns()
    print "End dns_consistency test"
    print "Start Evaluate DNS Flags"
    dns_to_flag()
    print "End Evaluate DNS Flags"
