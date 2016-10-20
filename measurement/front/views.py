from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.views import generic
from django.db import connections
from django.db.models import Q
from measurement.models import DNS
import json


# DNSTestKey Object #
# Parser test key object #
# Input: Json string obj #

class DNSTestKey(object):
    """docstring for TestKey"""
    def __init__(self, j):
        self.__dict__ = json.loads(j)

    def get_queries(self):
        return self.queries

    def get_resolver(self):
        return self.control_resolver

    def get_errors(self):
        return self.errors

    def get_isp_sonda(self):
        return self.annotations['isp']

    def ignore_data(self, list_public_dns=None):

        try:
            sonda_isp = self.get_isp_sonda()

            # Encontrar lista de ips #
            # del proveedor de la sonda_isp #
            # Output: lista de ips #
            ips_required = [dns.ip
                            for dns in
                            DNS.objects.filter(Q(isp=sonda_isp) |
                                               Q(isp='digitel'))]

            # Dejar ips de la lista de ips_required #
            self.left_data_from_list(ips_required)

            # Ignorar ips que esten registrados #
            # como de acceso publico #
            if list_public_dns:

                self.ignore_data_from_list(list_public_dns)

            return True

        except Exception:

            return False

    def ignore_data_from_list(self, list_ip):

        self.successful = [ip
                           for ip in self.successful
                           if self.successful and
                           ip not in list_ip]

        self.failed = [ip for ip in self.failed
                       if self.failed and ip not in list_ip]

        self.inconsistent = [ip
                             for ip in self.inconsistent
                             if self.inconsistent and
                             ip not in list_ip]

        if self.errors:
            for ip in list_ip:
                self.errors.pop(ip, None)

        if self.queries:
            for q in self.queries:
                if self.queries[0] == q:
                    pass
                elif q['resolver_hostname'] in list_ip:
                    q.pop('resolver_hostname', None)
                    q.pop('resolver_port', None)
                    q.pop('query_type', None)
                    q.pop('hostname', None)
                    q.pop('failure', None)
                    q.pop('answers', None)

            self.queries = filter(None, self.queries)

    def left_data_from_list(self, list_ip):

        self.successful = [ip
                           for ip in self.successful
                           if self.successful and ip in list_ip]

        self.failed = [ip for ip in self.failed
                       if self.failed and ip in list_ip]
        self.inconsistent = [ip
                             for ip in self.inconsistent
                             if self.inconsistent and ip in list_ip]

        if self.errors:
            for ip in list_ip:
                self.errors.pop(ip, None)

        if self.queries:
            for q in self.queries:
                if self.queries[0] == q:
                    pass
                elif q['resolver_hostname'] not in list_ip:
                    q.pop('resolver_hostname', None)
                    q.pop('resolver_port', None)
                    q.pop('query_type', None)
                    q.pop('hostname', None)
                    q.pop('failure', None)
                    q.pop('answers', None)

            self.queries = filter(None, self.queries)


class MeasurementTableView(generic.TemplateView):

    template_name = 'display_table.html'

    def get_context_data(self, **kwargs):

        context = super(MeasurementTableView, self).get_context_data(**kwargs)

        try:
            cursor = connections['titan_db'].cursor()

            cursor.execute("select * from metrics")
            columns = [col[0] for col in cursor.description]

            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            context['rows'] = rows
            context['columns'] = columns

        finally:
            connections['titan_db'].close()

        return context


class DNSTableView(generic.TemplateView):

    template_name = 'display_dns_table.html'

    def get_context_data(self, **kwargs):

        context = super(DNSTableView, self).get_context_data(**kwargs)

        try:
            cursor = connections['titan_db'].cursor()
            query = "select id, input, test_keys, measurement_start_time "
            query += "from metrics where test_name='dns_consistency' "
            cursor.execute(query)
            columns = [col[0].encode("ascii", "ignore")
                       for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Adding columns
            columns_final = columns[:len(columns) / 2]
            columns_final += ['match', 'dns isp',
                              'control result',
                              'dns name', 'dns result']
            columns_final += columns[len(columns) / 2:]
            columns_final.remove('test_keys')

            # Answers
            ans = []

            for row in rows:

                test_key = DNSTestKey(json.dumps(row['test_keys']))
                dns_isp = test_key.get_isp_sonda()
                public_dns = [dns.ip
                              for dns in DNS.objects.filter(public=True)]

                if test_key.ignore_data(public_dns):

                    queries = test_key.get_queries()
                    answers = queries[0]['answers']

                    for a in answers:
                        if a['answer_type'] == 'A':
                            control_resolver = a['ipv4']

                    for query in queries:

                        dns_name = query['resolver_hostname']

                        if query['failure']:
                            dns_result = query['failure']
                            match = False
                        else:

                            answers = query['answers']

                            for a in answers:
                                if a['answer_type'] == 'A':
                                    dns_result = a['ipv4']

                            if control_resolver == dns_result:
                                match = True
                            else:
                                match = False

                        if DNS.objects.filter(ip=dns_name).exists():
                            dns_table_name = DNS.objects\
                                                .get(ip=dns_name).verbose
                        else:
                            dns_table_name = dns_name

                        ans += [[row['id'], row['input'],
                                match, dns_isp, control_resolver,
                                dns_table_name, dns_result,
                                row['measurement_start_time']]]

            context['rows'] = [dict(zip(columns_final, row)) for row in ans]
            context['columns'] = columns_final

        finally:
            connections['titan_db'].close()

        return context


class PruebaDataTable(LoginRequiredMixin, generic.TemplateView):

    template_name = 'list.html'

    def get(self, request, *args, **kwargs):

        logout(request)
        print "done"

        return super(PruebaDataTable, self).get(request, *args, **kwargs)
