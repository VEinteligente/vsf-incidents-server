from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.views import generic
from django.db import connections
from django.db.models import Q
from measurement.models import DNS
import json


class DNSTestKey(object):
    """docstring for TestKey"""
    # def __init__(self, json):
    #     self.resolver = json['control_resolver']
    #     self.errors = json['errors']
    #     self.successful = json['successful']
    #     self.failed = json['failed']
    #     self.inconsistent = json['inconsistent']
    #     self.queries = json['queries']
    #     self.sonda = json['annotations']

    #     super(DNSTestKey, self).__init__()

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

            # Encontrar lista de ips de los proveedores que sean de la sonda_isp
            # Output: lista de objetos DNS
            ips = DNS.objects.filter(~Q(isp=sonda_isp) & ~Q(isp='digitel'))

            for isp in ips:
                if self.successful and isp in self.successful:
                    self.successful = self.successful.remove(isp.ip)
                if self.failed and isp in self.failed:
                    self.failed = self.failed.remove(isp.ip)
                if self.inconsistent and isp in self.inconsistent:
                    self.inconsistent = self.inconsistent.remove(isp.ip)
                if self.errors:
                    self.errors.pop(isp.ip, None)
                if self.queries:
                    for q in self.queries:
                        if isp.ip == q['resolver_hostname']:
                            self.queries.remove(q)

            # Filtrar por la lista de public dns
            if list_public_dns:

                for ip in list_public_dns:
                    if self.successful and ip in self.successful:
                        self.successful = self.successful.remove(ip)
                    if self.failed and ip in self.failed:
                        self.failed = self.failed.remove(ip)
                    if self.inconsistent and ip in self.inconsistent:
                        self.inconsistent = self.inconsistent.remove(ip)
                    if self.errors:
                        self.errors.pop(ip, None)
                    if self.queries:
                        for q in self.queries:
                            if ip == q['resolver_hostname']:
                                self.queries.remove(q)

            return True

        except Exception:

            return False



class MeasurementTableView(generic.TemplateView):

    template_name = 'display_table.html'

    def get_context_data(self, **kwargs):

        context = super(MeasurementTableView,self).get_context_data(**kwargs)

        try:
            cursor = connections['titan_db'].cursor()

            cursor.execute("select * from metrics LIMIT 59")
            columns = [col[0] for col in cursor.description]

            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            # rows = cursor.fetchall()

            context['rows'] = rows
            context['columns'] = columns

        finally:
            connections['titan_db'].close()

        return context


class DNSTableView(generic.TemplateView):

    template_name = 'display_dns_table.html'

    def get_context_data(self, **kwargs):

        context = super(DNSTableView,self).get_context_data(**kwargs)

        try:
            cursor = connections['titan_db'].cursor()
            query = "select id, input, test_keys, measurement_start_time "
            query += "from metrics where test_name='dns_consistency' "
            query += "limit 100"
            cursor.execute(query)
            columns = [col[0].encode("ascii","ignore") for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Adding columns
            columns_final = columns[:len(columns)/2]
            columns_final += ['dns isp','control result','dns name', 'dns result'] 
            columns_final += columns[len(columns)/2:]
            columns_final.remove('test_keys')

            # Answers
            ans = []

            for row in rows:
                test_key = DNSTestKey(json.dumps(row['test_keys']))
                dns_isp = test_key.get_isp_sonda()
                control_resolver = test_key.get_resolver()

                if test_key.ignore_data():

                    queries = test_key.get_queries()

                    for query in queries:

                        dns_name = query['resolver_hostname']

                        if DNS.objects.filter(ip=dns_name).exists():
                            dns_table_name = DNS.objects.get(ip=dns_name).verbose
                        else:
                            dns_table_name = dns_name

                        dns_result = query['failure']

                        ans += [[row['id'], row['input'], 
                                dns_isp, control_resolver,
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
