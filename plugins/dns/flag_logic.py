from django.db.models.expressions import RawSQL

from measurement.models import Metric
from plugins.dns.models import DNS


def web_connectivity_to_dns():
    pass


def dns_consistency_to_dns():
    # Get all metrics with test_name dns_consistency
    # but only values measurement, test_keys->'queries'
    # and test_keys->'control_resolver'

    dns_consistency_metrics = Metric.objects.filter(
        test_name='dns_consistency'
    ).annotate(
        queries=RawSQL(
            "test_keys->'queries'", ()
        ),
        control_resolver=RawSQL(
            "test_keys->'control_resolver'", ()
        )
    ).values(
        'id',
        'measurement',
        'queries',
        'control_resolver'
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
                dns_exist = DNS.objects.filter(
                    metric_id=dns_metric['id'],
                    control_resolver_resolver_hostname=cr['resolver_hostname'],
                    resolver_hostname=query['resolver_hostname']
                ).exists()
                if not dns_exist:
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


def metric_to_dns():
    print "Start Web_connectivity test"
    web_connectivity_to_dns()
    print "End Web_connectivity test"
    print "Start dns_consistency test"
    dns_consistency_to_dns()
    print "End dns_consistency test"


