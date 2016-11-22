from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from datetime import datetime
from measurement.models import Flag, DNS, Metric
from django.db.models import (
    Q, Count, Case, When, CharField
)
from measurement.front.views import DBconnection, DNSTestKey
import json
from vsf import conf

# Create your views here.


class UpdateFlagView(generic.UpdateView):
    """docstring for UpdateFlagView"""
    model = Flag

    def get(self, request, *args, **kwargs):

        try:
            # List of 'medicion' of Flags #
            list_dns = self.model.objects.using('default')\
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
            result_dns = database.db_execute(query_dns)
            result_tcp = database.db_execute(query_tcp)

            rows_dns = {}
            rows_tcp = {}

            if result_dns:

                rows_dns = result_dns['rows']

            if result_tcp:

                rows_tcp = result_tcp['rows']

            # Update DNS Flags #
            update_dns = self.update_dns_flags(rows_dns)

            # Update TCP Flags #
            update_tcp = self.update_tcp_flags(rows_tcp)

            # Update HTTP Flags #
            update_http = self.update_http_flags(rows_tcp)

            # Update Hard Flags #
            update_hard_flags = self.update_hard_flags()

            if update_dns and update_tcp and update_http and update_hard_flags:

                return HttpResponse(status=200)

        except Exception as e:

            print e

            return HttpResponse(status=400)

    def update_dns_flags(self, rows):

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))

            # Get public DNS #
            dns_isp = 'cantv'
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

                        # If query doesn't has failure, then find dns result #
                        # from answer type A and later compare it with control #
                        # resolver #
                        if query['failure']:

                            if not Flag.objects.filter(medicion=row['id'],
                                                       ip=dns_name,
                                                       type_med='DNS').exists():

                                flag = Flag.objects.create(medicion=row['id'],
                                                           date=date,
                                                           target=row['input'],
                                                           isp=dns_isp,
                                                           region='CCS',
                                                           ip=dns_name,
                                                           type_med='DNS')
                                flag.save(using='default')                               

                        else:

                            answers = query['answers']

                            for a in answers:
                                if a['answer_type'] == 'A' and \
                                   a['ipv4'] not in dns_result:
                                    dns_result += a['ipv4']

                            # If doesn't match, generate soft flag in measurement #
                            #if control_resolver != dns_result:
                            if not all(map(lambda v: v in control_resolver, dns_result)):

                                if not Flag.objects.filter(ip=dns_name,
                                                           medicion=row['id'],
                                                           type_med='DNS').exists():

                                    flag = Flag.objects.create(ip=dns_name,
                                                               date=date,
                                                               target=row['input'],
                                                               isp=dns_isp,
                                                               region='CCS',
                                                               medicion=row['id'],
                                                               type_med='DNS')
                                    flag.save(using='default')

        return True

    def update_tcp_flags(self, rows):

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))
            tcp_connect = test_key.get_tcp_connect()

            date = row['measurement_start_time']

            for tcp in tcp_connect:

                if tcp['status']['blocked']:

                    if not Flag.objects.filter(ip=tcp['ip'],
                                               medicion=row['id'],
                                               type_med='TCP').exists():

                        flag = Flag.objects.create(ip=tcp['ip'],
                                                   date=date,
                                                   target=row['input'],
                                                   isp='cantv',
                                                   region='CCS',
                                                   medicion=row['id'],
                                                   type_med='TCP')
                        flag.save(using='default')

        return True

    def update_http_flags(self, rows):

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))

            date = row['measurement_start_time']

            if not test_key.get_headers_match() and \
               not test_key.get_body_length_match() or \
               not test_key.get_status_code_match():

                if not Flag.objects.filter(ip=test_key.get_client_resolver(),
                                           medicion=row['id'],
                                           type_med='HTTP').exists():

                    flag = Flag.objects.create(ip=test_key.get_client_resolver(),
                                               date=date,
                                               target=row['input'],
                                               isp='cantv',
                                               region='CCS',
                                               medicion=row['id'],
                                               type_med='HTTP')
                    flag.save(using='default')

        return True

    def update_hard_flags(self):

        # Evaluating first condition for hard flags
        ids = Metric.objects.values_list('report_id',flat=True)
        ids = list(reversed(ids))[:conf.LAST_REPORTS_Y1]

        flags = Flag.objects\
                    .filter(medicion__in=ids)

        result = flags\
                     .values('isp','target','type_med')\
                     .annotate(total_soft=Count(Case(
                               When(flag=False, then=1),
                               output_field=CharField())))\
                     .filter(total_soft=conf.SOFT_FLAG_REPEATED_X1)

        if result:

            for r in result:
                flags_to_update = flags.filter(isp=r['isp'],
                                               target=r['target'],
                                               type_med=r['type_med'])

                map(self.soft_to_hard_flag, flags_to_update)

        else:

            # Evaluating second condition for hard flags
            ids = Metric.objects.values_list('report_id',flat=True)
            ids = list(reversed(ids))[:conf.LAST_REPORTS_Y2]

            flags = Flag.objects\
                    .filter(medicion__in=ids)

            result = flags\
                         .values('isp','target','type_med','region')\
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

                    map(self.soft_to_hard_flag, flags_to_update)

        return True

    def soft_to_hard_flag(self, flag):
        flag.flag = True
        flag.save(using='default')
