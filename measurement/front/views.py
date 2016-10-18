from django.shortcuts import render
from django.views import generic
from django.db import connections

class DNSTestKey(object):
    """docstring for TestKey"""
    def __init__(self, json):
        self.resolver = json['control_resolver']
        self.errors = json['errors']
        self.successful = json['successful']
        self.failed = json['failed']
        self.inconsistent = json['inconsistent']
        self.queries = json['queries']
        self.sonda = json['annotations']

        super(DNSTestKey, self).__init__()

    def get_queries(self):
        return self.queries

    def get_resolver(self):
        return self.resolver

    def get_errors(self):
        return self.errors

    def ignore_data(self, list_public_dns=None):

        try:
            sonda_isp = self.sonda['isp']
            # Encontrar lista de ips de los proveedores que no sean los de la sonda_isp
            # Output: una lista de ips
            ips = ['200.35.65.3', '200.35.65.4', 
                   '200.82.134.7', '200.82.134.8', 
                   '200.35.192.7', '200.35.192.9']

            for ip in ips:
                if self.successful and ip in self.successful:
                    self.successful = self.successful.remove(ip)
                if self.failed and ip in self.failed:
                    self.failed = self.failed.remove(ip)
                if self.inconsistent and ip in self.inconsistent:
                    self.inconsistent = self.inconsistent.remove(ip)
                if self.errors:
                    self.errors.pop(ip, None)

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
            query += "limit 2"
            cursor.execute(query)
            columns = [col[0].encode("ascii","ignore") for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Answers
            ans = []

            for row in rows:
                test_key = DNSTestKey(row['test_keys'])


            context['rows'] = rows
            context['columns'] = columns

        finally:
            connections['titan_db'].close()

        return context


class PruebaDataTable(generic.TemplateView):

    template_name = 'list.html'
