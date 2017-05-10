import json

from django.db.models import (
    Count,
    Case,
    When,
    CharField
)

from event.models import (
    Target,
    MutedInput
)
from event.utils import (
    suggestedEvents
)
from measurement.front.views import DBconnection, DNSTestKey
from measurement.models import (
    Flag,
    DNS,
    Metric,
    Probe
)
from vsf import conf


def update_dns_flags(rows):

    for row in rows:

        # Convert json test_keys into python object
        test_key = DNSTestKey(json.dumps(row['test_keys']))

        # Get public DNS #
        if 'annotation' in row:
            probe = Probe.objects.get(identification=row['annotation']['probe'])
            dns_isp = probe.isp
        else:
            dns_isp = None

        url, created = Target.objects\
                          .get_or_create(url=row['input'])

        # dns_isp = 'cantv' # POR AHORA
        public_dns = [dns.ip
                      for dns in DNS.objects.filter(public=True)]

        date = row['measurement_start_time']

        # Ignore data from test_key #
        if test_key.ignore_data(dns_isp, public_dns):

            # Get queries #
            queries = test_key.get_queries()

            if not queries[0]['failure'] and queries[0]['answers']:

                # Get answers #
                answers = queries[0]['answers']
                control_resolver = []
                dns_result = []

                # Get control resolver from answer_type A #
                for a in answers:
                    if a['answer_type'] == 'A' and \
                       a['ipv4'] not in control_resolver:
                        control_resolver += a['ipv4']

                # Verify each result from queries with control resolver #
                for query in queries:

                    dns_name = query['resolver_hostname']

                    # If dns_name is in DNS table, find its isp #
                    if DNS.objects.filter(ip=dns_name).exists():
                        dns_isp = DNS.objects\
                                     .get(ip=dns_name).isp

                    # If query doesn't has failure, then find dns result #
                    # from answer type A and later compare it with control #
                    # resolver #
                    if query['failure']:

                        if not Flag.objects.filter(medicion=row['id'],
                                                   ip=dns_name,
                                                   type_med='DNS').exists():

                            flag = False

                            if dns_isp is None:
                                dns_isp = 'Unknown'
                                flag = None

                            flag = Flag.objects.create(medicion=row['id'],
                                                       date=date,
                                                       target=url,
                                                       isp=dns_isp,
                                                       region='CCS',
                                                       ip=dns_name,
                                                       flag=flag,
                                                       type_med='DNS')
                            flag.save(using='default')

                    else:

                        answers = query['answers']

                        for a in answers:
                            if a['answer_type'] == 'A' and \
                               a['ipv4'] not in dns_result:
                                dns_result += a['ipv4']

                        # If doesn't match, generate soft flag in measurement #
                        # if control_resolver != dns_result:
                        if not all(map(lambda v: v in control_resolver, dns_result)):

                            if not Flag.objects.filter(ip=dns_name,
                                                       medicion=row['id'],
                                                       type_med='DNS').exists():

                                flag = False

                                if dns_isp is None:
                                    dns_isp = 'Unknown'
                                    flag = None

                                flag = Flag.objects.create(ip=dns_name,
                                                           flag=flag,
                                                           date=date,
                                                           target=url,
                                                           isp=dns_isp,
                                                           region='CCS',
                                                           medicion=row['id'],
                                                           type_med='DNS')
                                flag.save(using='default')

    return True


def update_tcp_flags(rows):

    for row in rows:

        # Convert json test_keys into python object
        test_key = DNSTestKey(json.dumps(row['test_keys']))
        tcp_connect = test_key.get_tcp_connect()

        date = row['measurement_start_time']

        if 'annotation' in row:
            probe = Probe.objects.get(identification=row['annotation']['probe'])
            dns_isp = probe.isp
        else:
            dns_isp = None

        url, created = Target.objects\
                          .get_or_create(url=row['input'])

        for tcp in tcp_connect:

            if tcp['status']['blocked']:

                if not Flag.objects.filter(ip=tcp['ip'],
                                           medicion=row['id'],
                                           type_med='TCP').exists():

                    flag = False

                    if dns_isp is None:
                        dns_isp = 'Unknown'
                        flag = None

                    flag = Flag.objects.create(ip=tcp['ip'],
                                               flag=flag,
                                               date=date,
                                               target=url,
                                               isp=dns_isp,
                                               region='CCS',
                                               medicion=row['id'],
                                               type_med='TCP')
                    flag.save(using='default')

    return True


def update_http_flags(rows):

    for row in rows:

        # Convert json test_keys into python object
        test_key = DNSTestKey(json.dumps(row['test_keys']))

        date = row['measurement_start_time']

        if 'annotation' in row:
            probe = Probe.objects.get(identification=row['annotation']['probe'])
            dns_isp = probe.isp
        else:
            dns_isp = None

        url, created = Target.objects\
                          .get_or_create(url=row['input'])

        if not test_key.get_headers_match() and \
           not test_key.get_body_length_match() or \
           not test_key.get_status_code_match():

            if not Flag.objects.filter(ip=test_key.get_client_resolver(),
                                       medicion=row['id'],
                                       type_med='HTTP').exists():

                flag = False

                if dns_isp is None:
                    dns_isp = 'Unknown'
                    flag = None

                flag = Flag.objects.create(ip=test_key.get_client_resolver(),
                                           flag=flag,
                                           date=date,
                                           target=url,
                                           isp=dns_isp,
                                           region='CCS',
                                           medicion=row['id'],
                                           type_med='HTTP')
                flag.save(using='default')

    return True


def update_muted_flags():

    muted_list = MutedInput.objects.values_list('url')
    type_list = MutedInput.objects.values_list('type_med')

    flags = Flag.objects.filter(flag=False,
                                target__url__in=muted_list,
                                type_med__in=type_list)

    flags.update(flag=None)

    return True


def update_hard_flags():

    # Evaluating first condition for hard flags
    ids = Metric.objects.values_list('report_id', flat=True)
    ids = list(reversed(ids))[:conf.LAST_REPORTS_Y1]

    flags = Flag.objects\
                .filter(medicion__in=ids)

    result = flags\
        .values('isp', 'target', 'type_med')\
        .annotate(total_soft=Count(Case(
                           When(flag=False, then=1),
                           output_field=CharField())))\
        .filter(total_soft=conf.SOFT_FLAG_REPEATED_X1)

    if result:

        for r in result:
            flags_to_update = flags.filter(isp=r['isp'],
                                           target=r['target'],
                                           type_med=r['type_med'])

            map(soft_to_hard_flag, flags_to_update)

    else:

        # Evaluating second condition for hard flags
        ids = Metric.objects.values_list('report_id', flat=True)
        ids = list(reversed(ids))[:conf.LAST_REPORTS_Y2]

        flags = Flag.objects\
                    .filter(medicion__in=ids)

        result = flags\
            .values('isp', 'target', 'type_med', 'region')\
            .annotate(total_soft=Count(Case(
                              When(flag=False, then=1),
                              output_field=CharField())))\
            .filter(total_soft=conf.SOFT_FLAG_REPEATED_X2)

        if result:

            for r in result:
                flags_to_update = flags.filter(isp=r['isp'],
                                               target=r['target'],
                                               type_med=r['type_med'],
                                               region=r['region'])

                map(soft_to_hard_flag, flags_to_update)

    return True


def soft_to_hard_flag(flag):
    flag.flag = True
    flag.save(using='default')
    suggestedEvents(flag)


def update_flags_manual():
    try:
        print "entrando a la funcion"
        # List of 'medicion' of Flags #
        list_dns = Flag.objects.using('default')\
            .values_list('medicion', flat=True)\
            .order_by('medicion')\
            .distinct()

        # Create database object #
        database = DBconnection('titan_db')
        ids = None

        if list_dns:

            ids = '('

            for f in list_dns:
                if f == list_dns[len(list_dns) - 1]:
                    ids += '\'' + f + '\''
                else:
                    ids += '\'' + f + '\', '

            ids += ')'

        # Query for dns #
        query_dns = "select id, input, test_keys, measurement_start_time "
        query_dns += "from metrics where test_name='dns_consistency' "

        # Query for TCP flags #
        query_tcp = "select id, input, test_keys, measurement_start_time "
        query_tcp += "from metrics where test_name='web_connectivity' "

        if ids:
            query_dns += " and id not in " + ids
            query_tcp += " and id not in " + ids

        # Results from execute queries #
        print "antes del query for DNS"
        result_dns = database.db_execute(query_dns)
        print "Terminado el de DNS y antes del query for TCP"
        result_tcp = database.db_execute(query_tcp)
        print "Terminado el de TCP"

        rows_dns = {}
        rows_tcp = {}

        if result_dns:

            rows_dns = result_dns['rows']

        if result_tcp:

            rows_tcp = result_tcp['rows']

        print "update 1 update DNS"
        # Update DNS Flags #
        update_dns = update_dns_flags(rows_dns)

        print "update 2 Update TCP"
        # Update TCP Flags #
        update_tcp = update_tcp_flags(rows_tcp)

        print "update 3 Update HTTP"
        # Update HTTP Flags #
        update_http = update_http_flags(rows_tcp)

        print "update 4 Update Muted"
        # Update Muted Flags #
        update_muted = update_muted_flags()

        print "update 5 Update hard"
        # Update Hard Flags #
        update_hard = update_hard_flags()

        if update_dns and update_tcp and \
           update_http and update_hard and \
           update_muted:

            print "Fin"
            return "200 ok (="

    except Exception as e:

        print e

        return "400 error )="
