from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from measurement.models import Flag, DNS
from measurement.front.views import DBconnection, DNSTestKey
import json

# Create your views here.


class UpdateFlagView(generic.UpdateView):
    """docstring for UpdateFlagView"""
    model = Flag

    def get(self, request, *args, **kwargs):

        try:
            queryset = self.model.objects.using('default').all()

            # Create database object #
            database = DBconnection('titan_db')
            ids = None

            if queryset:

                ids = '('

                for f in queryset:
                    if f.medicion == queryset[len(queryset)-1].medicion:
                        ids += '\'' + f.medicion + '\''
                    else:
                        ids += '\'' + f.medicion + '\', '

                ids += ')'

            # Query for dns #
            query_dns = "select id, test_keys "
            query_dns += "from metrics where test_name='dns_consistency' "

            # Query for TCP flags #
            query_tcp = "select id, test_keys "
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

            if update_dns and update_tcp:

                return HttpResponse(status=200)

        except Exception as e:

            print e

            return HttpResponse(status=400)

    def update_dns_flags(self, rows):

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))

            # Get public DNS #
            public_dns = [dns.ip
                          for dns in DNS.objects.filter(public=True)]

            # Ignore data from test_key #
            if test_key.ignore_data(public_dns):

                # Get queries #
                queries = test_key.get_queries()

                # Get answers #
                answers = queries[0]['answers']

                # Get control resolver from answer_type A #
                for a in answers:
                    if a['answer_type'] == 'A':
                        control_resolver = a['ipv4']

                # Verify each result from queries with control resolver #
                for query in queries:

                    dns_name = query['resolver_hostname']

                    # If query doesn't has failure, then find dns result #
                    # from answer type A and later compare it with control #
                    # resolver #

                    if not query['failure']:

                        answers = query['answers']

                        for a in answers:
                            if a['answer_type'] == 'A':
                                dns_result = a['ipv4']

                        # If doesn't match, generate soft flag in measurement #
                        if control_resolver != dns_result:
                            flag = Flag.objects.create(ip=dns_name,
                                                       medicion=row['id'],
                                                       type_med='DNS')
                            flag.save(using='default')

        return True

    def update_tcp_flags(self, rows):

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))
            tcp_connect = test_key.get_tcp_connect()

            for tcp in tcp_connect:

                if tcp['status']['blocked']:
                    flag = Flag.objects.create(ip=tcp['ip'],
                                               medicion=row['id'],
                                               type_med='TCP')
                    flag.save(using='default')

        return True
