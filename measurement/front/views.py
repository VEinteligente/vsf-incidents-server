from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse_lazy
from django.core.mail import EmailMessage
from django.views import generic
from django.db import connections
from django.db.models import Q, Prefetch
from eztables.views import DatatablesView
from measurement.models import (
    DNSServer,
    Flag,
    Metric,
    Probe
)
from measurement.front.forms import (
    MutedInputForm,
    ProbeForm,
    ManualFlagForm,
    MeasurementToEventForm
)
from event.models import Target, MutedInput, Country, State, ISP, Plan
from event.utils import suggestedEvents
from measurement.utils import *
from plugins.views import PluginTableView
from plugins.dns.models import DNS as DNS_METRIC
from plugins.tcp.models import TCP
from plugins.http.models import HTTP
from plugins.ndt.models import NDT as NDT
import re
import json
from django.db.models.expressions import RawSQL

import logging

from dashboard.mixins import PageTitleMixin

logger = logging.getLogger('')

RE_FORMATTED = re.compile(r'\{(\w+)\}')


class DBconnection(object):
    """Database connection object.

    Attributes:
        db_name (str): Database name.
    """
    def __init__(self, db_name):
        self.db_name = db_name

    def db_execute(self, query):
        """Execute a query in the database.

        Args:
            query (str): SQL query

        Returns:
            dict: A dictionary with data for columns and rows
        """
        try:
            cursor = connections[self.db_name].cursor()

            cursor.execute(query)
            columns = [col[0].encode("ascii", "ignore")
                       for col in cursor.description]

            rows = [dict(zip(columns, row))
                    for row in cursor.fetchall()]

            return {'columns': columns, 'rows': rows}

        except Exception as e:
            print e

        finally:
            connections['titan_db'].close()


class DNSTestKey(object):
    """Test key object from json string object."""
    def __init__(self, j):
        self.__dict__ = json.loads(j)

    def get_queries(self):
        """Execute a query in the database.
        Returns:
            dict: A list of dicts with data from test_keys
                  queries
        """
        if self.queries:
            return self.queries
        else:
            return []

    def get_resolver(self):
        """Get Control Resolver value in Test key object
        Returns:
            string: control resolver value
        """
        if self.control_resolver:
            return self.control_resolver

    def get_client_resolver(self):
        """Get Client Resolver value in Test key object
        Returns:
            string: client resolver value
        """
        if self.client_resolver:
            return self.client_resolver

    def get_headers_match(self):
        """Get Header Match value in Test key object
        Returns:
            string: header match value
        """
        if self.headers_match:
            return self.headers_match

    def get_body_length_match(self):
        """Get Body Length Match value in Test key object
        Returns:
            int: body length match value
        """
        if self.body_length_match:
            return self.body_length_match

    def get_status_code_match(self):
        """Get Status Code Match value in Test key object
        Returns:
            string: status code match value
        """
        if self.status_code_match:
            return self.status_code_match

    def get_errors(self):
        """Get posible error dict in Test key object
        Returns:
            dict: A dictionary with all possible errors
        """
        if self.errors:
            return self.errors
        else:
            return {}

    def get_tcp_connect(self):
        """Get TCP connections list in Test key object
        Returns:
            list: list of TCP connections
        """
        if self.tcp_connect:
            return self.tcp_connect
        else:
            return []

    def ignore_data(self, sonda_isp, list_public_dns=None):
        """Filter every object with probe ISP in list
        Args:
            list_public_dns: List of public DNS to ignore
        """
        try:
            # Find ip list #
            # from sonda_isp provider #
            # Output: ip list #
            if sonda_isp:
                ips_required = [dns.ip
                                for dns in
                                DNSServer.objects.filter(Q(isp=sonda_isp) |
                                                         Q(isp='digitel'))]
            else:
                ips_required = [dns.ip
                                for dns in
                                DNSServer.objects.filter(Q(isp='digitel'))]

            if list_public_dns:

                self.ignore_data_from_list(list_public_dns)

            return True

        except Exception:

            return False

    def ignore_data_from_list(self, list_ip):
        """Filter every object with diferent IP in list
        Args:
            list_ip: List of IP to ignore
        """

        # Get successful ips not in list_ip #
        self.successful = [ip
                           for ip in self.successful
                           if self.successful and
                           ip not in list_ip]

        # Get failed ips not in list_ip #
        self.failures = [ip for ip in self.failures
                       if self.failures and ip not in list_ip]

        # Get inconsistent ips not in list_ip #
        self.inconsistent = [ip
                             for ip in self.inconsistent
                             if self.inconsistent and
                             ip not in list_ip]

        # Get errors ips not in list_ip #
        if self.errors:
            for ip in list_ip:
                self.errors.pop(ip, None)

        # Get queries with ips not in list_ip #
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
        """Filter every object with IP in list
        Args:
            list_ip: List of IP to ignore
        """

        # Get successful ips in list_ip #
        self.successful = [ip
                           for ip in self.successful
                           if self.successful and ip in list_ip]

        # Get failed ips in list_ip #
        self.failures = [ip for ip in self.failures
                         if self.failures and ip in list_ip]

        # Get inconsistent ips in list_ip #
        self.inconsistent = [ip
                             for ip in self.inconsistent
                             if self.inconsistent and ip in list_ip]

        # Get errors ips in list_ip #
        if self.errors:
            for ip in list_ip:
                pass
                self.errors.pop(ip, None)

        # Get queries without ips not in list_ip #
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


class MetricTableView(PluginTableView):
    page_header = "Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurement", "All"]
    titles = [
        'checkbox',
        'flag',
        'manual_flag',
        'status blocked',
        'status failure',
        'status success',
        'test keys',
        'measurement',
        'input',
        'measurement_start_time',
        'report_id',
        'probe id',
        'probe ISP'
    ]
    url_ajax = '/measurement/metric-ajax/'


class MetricAjaxView(DatatablesView):
    fields = {
        'checkbox': 'metric__input',
        'flag': 'flag__flag',
        'manual flag': 'flag__manual_flag',
        'status blocked': 'status_blocked',
        'status failure': 'status_failure',
        'status success': 'status_success',
        'test keys': 'metric__test_keys',
        'measurement': 'metric__measurement',
        'input': 'metric__input',
        'measurement_start_time': 'metric__measurement_start_time',
        'report_id': 'metric__report_id',
        'probe id': 'metric__probe__identification',
        'probe ISP': 'metric__probe__isp__name'

    }

    queryset = Flag.objects.all().prefetch_related(
        Prefetch(
            'dnss',
            queryset=DNS_METRIC.objects.select_related('metric'),
            to_attr='dns_metrics'
        ),
        Prefetch(
            'https',
            queryset=HTTP.objects.select_related('metric'),
            to_attr='http_metrics'
        ),
        Prefetch(
            'tcps',
            queryset=TCP.objects.select_related('metric'),
            to_attr='tcp_metrics'
        ),
        Prefetch(
            'ndts',
            queryset=NDT.objects.select_related('metric'),
            to_attr='ndt_metrics'
        ),
    )

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )


class MeasurementTableView(LoginRequiredMixin, PageTitleMixin,
                           generic.TemplateView, generic.edit.FormMixin):
    """MeasurementTableView: TemplateView than
    display a list of all metrics in DB"""

    page_header = "Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurements", "All"]
    form_class = ManualFlagForm
    template_name = 'display_table.html'


class MeasurementAjaxView(DatatablesView):
    fields = {
        'checkbox': 'uuid',
        'Flag': 'flag',
        'manual_flag': 'manual_flag',
        'flag_id': 'uuid',
        'probe_isp': 'metric__probe__isp__name',
        'input': 'metric__input',
        'report_id': 'metric__report_id',
        'test_name': 'metric__test_name',
        'test_start_time': 'metric__test_start_time',
        'measurement_start_time': 'metric__measurement_start_time'
    }
    queryset = Flag.objects.all()

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )


class MeasurementDetail(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    model = Metric
    slug_url_kwarg = 'id'
    slug_field = 'measurement'
    template_name = 'detail_measurement.html'
    page_header = "Measurement Detail"
    page_header_description = ""
    context_object_name = "metric"

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        ctx = super(MeasurementDetail, self).get_context_data(**kwargs)

        return ctx


class DNSTableView(
    LoginRequiredMixin, PageTitleMixin,
    generic.TemplateView, generic.edit.FormMixin
):
    """DNSTableView: TemplateView than
    display a list of metrics in DB
    with dns_consistency as test_name"""

    page_header = "DNS Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurements", "DNS"]
    form_class = MeasurementToEventForm
    # template_name = 'display_dns_table.html'
    template_name = 'list_dns.html'

    # def get_context_data(self, **kwargs):

    #     context = super(DNSTableView, self).get_context_data(**kwargs)

    #     try:

    #         # Create database object #
    #         database = DBconnection('titan_db')
    #         query = "select id, input, test_keys, measurement_start_time "
    #         query += "from metrics where test_name='dns_consistency'"

    #         result = database.db_execute(query)
    #         rows = {}
    #         columns = {}

    #         if result:

    #             rows = result['rows']
    #             columns = result['columns']

    #         # Adding columns
    #         columns_final = ['flag'] + columns[:len(columns) / 2]
    #         columns_final += ['match', 'dns isp',
    #                           'control result',
    #                           'dns name', 'dns result']
    #         columns_final += columns[len(columns) / 2:]
    #         columns_final.remove('test_keys')

    #         # Answers
    #         ans = self.get_answers(rows)

    #         # Context data variables #
    #         context['rows'] = [dict(zip(columns_final, row)) for row in ans]
    #         context['columns'] = columns_final

    #     except Exception as e:
    #         print e

    #     return context

    # def get_answers(self, rows):
    #     """ Create from every row a Test Key object to
    #     extract the data to display in the list
    #     Args:
    #         rows: DB rows
    #     """

    #     ans = []

    #     for row in rows:

    #         # Convert json test_keys into python object
    #         test_key = DNSTestKey(json.dumps(row['test_keys']))

    #         # Get sonda isp and public DNS #
    #         if 'annotation' in row:
    #             probe = Probe.objects.get(identification=row['annotation']['probe'])
    #             dns_isp = probe.isp
    #         else:
    #             dns_isp = None

    #         if dns_isp is None:
    #             dns_isp = 'Unknown'

    #         # dns_isp = 'cantv' #VALOR MIENTRAS SE HACE TABLA DE SONDA
    #         public_dns = [dns.ip
    #                       for dns in DNS.objects.filter(public=True)]

    #         # Ignore data from test_key #
    #         if test_key.ignore_data(dns_isp, public_dns):

    #             # Get queries #
    #             queries = test_key.get_queries()

    #             if not queries[0]['failure'] and queries[0]['answers']:

    #                 # Get answers #
    #                 answers = queries[0]['answers']
    #                 control_resolver = []
    #                 dns_result = []

    #                 # Get control resolver from answer_type A #
    #                 for a in answers:
    #                     if a['answer_type'] == 'A' and \
    #                        a['ipv4'] not in control_resolver:
    #                         control_resolver += [a['ipv4']]

    #                 # Verify each result from queries with control resolver #
    #                 for query in queries:

    #                     dns_name = query['resolver_hostname']
    #                     match = False
    #                     flag_status = 'No flag'

    #                     # If query has failure, dns result #
    #                     # is a failure response and match is False #

    #                     # If query doesn't has failure, then find dns result #
    #                     # from answer type A and later compare it with control #
    #                     # resolver. If both are the same, match is True otherwise #
    #                     # match is False #

    #                     if query['failure']:
    #                         dns_result += query['failure']

    #                     answers = query['answers']

    #                     for a in answers:
    #                         if a['answer_type'] == 'A' and \
    #                            a['ipv4'] not in dns_result:
    #                             dns_result += [a['ipv4']]

    #                     if all(map(lambda v: v in control_resolver, dns_result)):
    #                         match = True
    #                     else:
    #                         # Search flag #

    #                         if Flag.objects.filter(ip=dns_name,
    #                                                medicion=row['id'],
    #                                                type_med='DNS').exists():

    #                             f = Flag.objects.get(ip=dns_name,
    #                                                  medicion=row['id'],
    #                                                  type_med='DNS')

    #                             if f.flag:
    #                                 flag_status = 'hard'
    #                             elif f.flag is False:
    #                                 flag_status = 'soft'
    #                             elif f.flag is None:
    #                                 flag_status = 'muted'

    #                     # If dns_name is in DNS table, find its name #
    #                     if DNS.objects.filter(ip=dns_name).exists():
    #                         dns_table_name = DNS.objects\
    #                                             .get(ip=dns_name).verbose
    #                     else:
    #                         dns_table_name = dns_name

    #                     #print control_resolver
    #                     #print sdns_result
    #                     # Formating the answers #
    #                     ans += [[flag_status, row['id'], row['input'],
    #                             match, dns_isp,','.join(control_resolver),
    #                             dns_table_name,','.join(dns_result),
    #                             row['measurement_start_time']]]

    #     return ans

    def get_context_data(self, **kwargs):

        context = super(DNSTableView, self).get_context_data(**kwargs)

        context['dns'] = json.dumps(list(DNSServer.objects.values('isp',
                                                            'ip',
                                                            'verbose')))
        context['dns_public'] = json.dumps(list(DNSServer.objects.values_list('ip', flat=True).filter(public=True)))
        context['probes'] = json.dumps(list(Probe.objects.values('identification','isp')))

        return context


class DNSTableAjax(DatatablesView):

    queryset = Metric.objects.filter(test_name='dns_consistency').annotate(
        annotation=RawSQL(
            "test_keys->>'annotation'", ()
        ),
        queries=RawSQL(
            "test_keys->'queries'", ()
        )
    )
    fields = {
        'checkbox': 'input',
        'Flag': 'id',
        'flag_id': 'id',
        'manual_flag': 'id',
        'ip': 'id',
        'annotation': 'annotation',
        'queries': 'queries',
        'id': 'id',
        'input': 'input',
        'match': 'id',
        'dns isp': 'id',
        'control resolver': 'id',
        'dns name': 'id',
        'dns result': 'id',
        'measurement_start_time': 'measurement_start_time',
        'report_id': 'report_id'
    }
    # queryset = Metric.objects.filter(test_name='dns_consistency')\
    #                          .annotate(
    #     # flag=connections['default'].cursor().execute(
    #     #     "SELECT flag FROM measurement_flag WHERE type_med='DNS'")
    #     # ,
    #     flag=RawSQL(
    #         "SELECT flag FROM vsf_db.measurement_flag WHERE type_med='DNS'", ()
    #     )
    # )

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )

    def get_rows(self, rows):
        """
        Format all rows
        """
        page_rows = [self.get_row(row) for row in rows]
        clone_rows = []

        metric_ids = []
        for row in page_rows:
            metric_ids.append(row['id'])

        flags = Flag.objects.filter(medicion__in=metric_ids)
        print flags
        for row in page_rows:
            row['flag_id'] = None
            row['manual_flag'] = None
            row['Flag'] = None
            # fill original rows with all data
            # from annotation and queries field
            try:
                probe = Probe.objects.get(
                    identification=row['annotation']['probe'])
                dns_isp = probe.isp
            except Exception:
                dns_isp = 'Unknown'
            row['dns isp'] = dns_isp

            queries = self.clean_queries_field(row['queries'])

            if not queries[0]['failure'] and queries[0]['answers']:
                # Get answers #
                answers = queries[0]['answers']
                control_resolver = []

                # Get control resolver from answer_type A #
                for a in answers:
                    if a['answer_type'] == 'A' and \
                       a['ipv4'] not in control_resolver:

                        control_resolver += [a['ipv4']]

                row['control resolver'] = control_resolver

                #Verify each result from queries with control resolver #
                for query in queries:

                    dns_result = []
                    dns_name = query['resolver_hostname']
                    match = False
                    # flag_status = 'No flag'

                    # If query has failure, dns result #
                    # is a failure response and match is False #

                    # If query doesn't has failure, then find dns result #
                    # from answer type A and later compare it with control #
                    # resolver. If both are the same, match is True otherwise #
                    # match is False #

                    if query['failure']:
                        dns_result += query['failure']

                    answers = query['answers']

                    for a in answers:
                        if a['answer_type'] == 'A' and \
                           a['ipv4'] not in dns_result:
                            dns_result += [a['ipv4']]

                    if all(map(lambda v: v in control_resolver, dns_result)):
                        match = True

                    # If dns_name is in DNS, find its name #
                    if DNSServer.objects.filter(ip=dns_name).exists():
                        dns_table_name = DNSServer.objects\
                                            .get(ip=dns_name).verbose
                    else:
                        dns_table_name = dns_name

                    if query == queries[0]:
                        row['dns name'] = dns_table_name
                        row['dns result'] = dns_result
                        row['match'] = match

                        if flags.filter(
                            medicion=row['id']
                        ).exists():

                            flag = flags.filter(
                                medicion=row['id']
                            ).first()
                            row['flag_id'] = flag.id
                            row['manual_flag'] = flag.manual_flag
                            row['Flag'] = flag.flag
                    else:
                        # Aqui voy a crear clones
                        clone_row = {}
                        clone_row['checkbox'] = row['checkbox']
                        clone_row['Flag'] = None
                        clone_row['flag_id'] = None
                        clone_row['manual_flag'] = None
                        clone_row['ip'] = row['ip']
                        clone_row['annotation'] = row['annotation']
                        clone_row['queries'] = row['queries']
                        clone_row['id'] = row['id']
                        clone_row['input'] = row['input']
                        clone_row['match'] = row['match']
                        clone_row['dns isp'] = row['dns isp']
                        clone_row['control resolver'] = row['control resolver']
                        clone_row['dns name'] = dns_table_name
                        clone_row['dns result'] = dns_result
                        clone_row['measurement_start_time'] = row[
                            'measurement_start_time']
                        clone_row['report_id'] = row['report_id']

                        if flags.filter(
                            medicion=row['id'],
                            ip=dns_name,
                            type_med='DNS'
                        ).exists():

                            flag = flags.filter(
                                medicion=row['id'],
                                ip=dns_name,
                                type_med='DNS'
                            ).first()
                            clone_row['flag_id'] = flag.id
                            clone_row['manual_flag'] = flag.manual_flag
                            clone_row['Flag'] = flag.flag

                        clone_rows.append(clone_row)
            else:
                row['match'] = False
                row['dns name'] = None
                row['dns result'] = None
                row['control resolver'] = None

        page_rows += clone_rows
        page_rows = sorted(page_rows, key=lambda k: k['id'])
        return page_rows

    def clean_queries_field(self, json_queries):
        public_dns = [dns.ip for dns in DNSServer.objects.filter(public=True)]

        queries = json_queries
        if queries:
            for q in queries:
                if queries[0] == q:
                    pass
                elif q['resolver_hostname'] in public_dns:
                    q.pop('resolver_hostname', None)
                    q.pop('resolver_port', None)
                    q.pop('query_type', None)
                    q.pop('hostname', None)
                    q.pop('failure', None)
                    q.pop('answers', None)

            queries = filter(None, queries)

        return queries


class TCPTableView(
    LoginRequiredMixin, PageTitleMixin,
    generic.TemplateView, generic.edit.FormMixin
):
    """TCPTableView: TemplateView than
    display a list of metrics in DB
    with web_connectivity as test_name"""

    page_header = "TCP Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurements", "TCP"]
    form_class = MeasurementToEventForm
    template_name = 'display_tcp_table.html'

    # def get_context_data(self, **kwargs):

    #     context = super(TCPTableView, self).get_context_data(**kwargs)

    #     try:
    #         # Create database connection #
    #         database = DBconnection('titan_db')
    #         query = "select id, input, test_keys, probe_cc, probe_ip, "
    #         query += "measurement_start_time "
    #         query += "from metrics where test_name='web_connectivity'"

    #         result = database.db_execute(query)

    #         rows = {}
    #         columns = {}

    #         if result:

    #             rows = result['rows']
    #             columns = result['columns']

    #         # Adding columns
    #         columns_final = ['flag'] + columns[:len(columns) / 2]
    #         columns_final += ['ip', 'port', 'bloqueado', 'medicion exitosa']
    #         columns_final += columns[len(columns) / 2:]
    #         columns_final.remove('test_keys')

    #         # Answers #
    #         ans = self.get_answers(rows)

    #         # Context data variables #
    #         context['rows'] = [dict(zip(columns_final, row)) for row in ans]
    #         context['columns'] = columns_final

    #     except Exception as e:

    #         print e

    #     return context

    # def get_answers(self, rows):
    #     """ Create from every row a Test Key object to
    #     extract the data to display in the list
    #     Args:
    #         rows: DB rows
    #     """
    #     ans = []

    #     for row in rows:

    #         # Convert json test_keys into python object
    #         test_key = DNSTestKey(json.dumps(row['test_keys']))
    #         tcp_connect = test_key.get_tcp_connect()

    #         for tcp in tcp_connect:

    #             flag_status = 'No flag'

    #             if Flag.objects.filter(ip=tcp['ip'],
    #                                    medicion=row['id'],
    #                                    type_med='TCP').exists():

    #                 f = Flag.objects.get(ip=tcp['ip'],
    #                                      medicion=row['id'],
    #                                      type_med='TCP')

    #                 if f.flag:
    #                     flag_status = 'hard'
    #                 elif f.flag is False:
    #                     flag_status = 'soft'
    #                 elif f.flag is None:
    #                     flag_status = 'muted'

    #             ip = tcp['ip']
    #             port = tcp['port']
    #             blocked = tcp['status']['blocked']
    #             success = tcp['status']['success']

    #             # Formating the answers #
    #             ans += [[flag_status, row['id'], row['input'],
    #                      ip, port, blocked, success,
    #                      row['probe_cc'], row['probe_ip'],
    #                      row['measurement_start_time']]]

    #     return ans


class TCPTableAjax(LoginRequiredMixin, DatatablesView):
    """TCPTableAjax: DatatablesView than
    populate a DataTable with all metrics with web_connectivity
    as test_name for tcp test"""

    # queryset = Metric.objects.filter(test_name='web_connectivity')
    queryset = Metric.objects.filter(test_name='web_connectivity').annotate(
        tcp_uu=RawSQL(
            "test_keys->'tcp_connect'", ()
        ),
    )
    fields = {
        'checkbox': 'id',
        'Flag': 'id',
        'flag_id': 'id',
        'manual_flag': 'id',
        'tcp': 'tcp_uu',
        'id': 'id',
        'input': 'input',
        'ip': 'id',
        'port': 'id',
        'blocked': 'id',
        'nam': 'id',
        'probe_cc': 'probe_cc',
        'probe_ip': 'probe_ip',
        'measurement_start_time': 'measurement_start_time',
        'report_id': 'report_id'
    }

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )

    def get_rows(self, rows):
        '''Format all rows'''
        page_rows = [self.get_row(row) for row in rows]
        clone_rows = []

        metric_ids = []
        for row in page_rows:
            metric_ids.append(row['id'])

        flags = Flag.objects.filter(medicion__in=metric_ids)

        for row in page_rows:
            row['flag_id'] = None
            row['manual_flag'] = None
            row['Flag'] = None
            tcp_connect = row['tcp']
            for tcp in tcp_connect:
                if tcp == tcp_connect[0]:

                    row['ip'] = tcp['ip']
                    row['port'] = tcp['port']
                    row['blocked'] = tcp['status']['blocked']
                    row['success'] = tcp['status']['success']
                    if flags.filter(
                        medicion=row['id'], ip=row['ip']
                    ).exists():

                        flag = flags.filter(
                            medicion=row['id'], ip=row['ip']
                        ).first()
                        row['flag_id'] = flag.id
                        row['manual_flag'] = flag.manual_flag
                        row['Flag'] = flag.flag


                else:
                    # Aqui voy a crear clones
                    clone_row = {}
                    clone_row['checkbox'] = row['checkbox']
                    clone_row['Flag'] = None
                    clone_row['flag_id'] = None
                    clone_row['manual_flag'] = None
                    clone_row['ip'] = tcp['ip']
                    clone_row['port'] = tcp['port']
                    clone_row['blocked'] = tcp['status']['blocked']
                    clone_row['id'] = row['id']
                    clone_row['input'] = row['input']
                    clone_row['tcp'] = row['tcp']
                    clone_row['probe_cc'] = row['probe_cc']
                    clone_row['probe_ip'] = row['probe_ip']
                    clone_row['success'] = tcp['status']['success']
                    clone_row['measurement_start_time'] = row[
                        'measurement_start_time']
                    clone_row['report_id'] = row['report_id']
                    if flags.filter(
                        medicion=row['id'],
                        ip=tcp['ip'],
                        type_med='TCP'
                    ).exists():
                        print "hola entre"
                        flag = flags.filter(
                            medicion=row['id'],
                            ip=tcp['ip'],
                        type_med='TCP'
                        ).first()
                        clone_row['flag_id'] = flag.id
                        clone_row['manual_flag'] = flag.manual_flag
                        clone_row['Flag'] = flag.flag

                    clone_rows.append(clone_row)

        page_rows += clone_rows
        page_rows = sorted(page_rows, key=lambda k: k['id'])
        return page_rows


class HTTPTableView(
    LoginRequiredMixin, PageTitleMixin,
    generic.TemplateView, generic.edit.FormMixin
):
    """HTTPTableView: TemplateView than
    display a list of metrics in DB using
    HTTPListDatatablesView"""

    page_header = "HTTP Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurements", "HTTP"]
    form_class = ManualFlagForm
    template_name = 'display_http_table.html'


class HTTPListDatatablesView(LoginRequiredMixin, DatatablesView):
    """HTTPListDatatablesView: DatatablesView than
    populate a DataTable with all metrics with web_connectivity
    as test_name"""

    queryset = Metric.objects.filter(
        Q(test_name='web_connectivity') | Q(test_name='http_header_field_manipulation') | Q(test_name='http_invalid_request_line')
    ).annotate(
        body_length_match=RawSQL(
            "test_keys->>'body_length_match'", ()
        ),
        body_proportion=RawSQL(
            "test_keys->>'body_proportion'", ()
        ),
        headers_match=RawSQL(
            "test_keys->>'headers_match'", ()
        ),
        status_code_match=RawSQL(
            "test_keys->>'status_code_match'", ()
        ),
        title_match=RawSQL(
            "test_keys->>'title_match'", ()
        )
    )
    fields = {
        'checkbox': 'input',
        'Flag': 'flags__flag',
        'manual_flag': 'flags__manual_flag',
        'flag_id': 'flags__id',
        'id': 'id',
        'measurement_start_time': 'measurement_start_time',
        'input': 'input',
        'probe_cc': 'probe_cc',
        'body_length_match': 'body_length_match',
        'body_proportion': 'body_proportion',
        'headers_match': 'headers_match',
        'status_code_match': 'status_code_match',
        'title_match': 'title_match',
        'report_id': 'report_id',
        'test_name': 'test_name'
    }

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )


# Muted Input CRUD

class ListMutedInput(LoginRequiredMixin, PageTitleMixin, generic.ListView):
    """ListMutedInput: ListView than
    display a list of all muted inputs"""
    model = MutedInput
    template_name = "list_muted.html"
    context_object_name = "mutes"
    page_header = "Muted Inputs"
    page_header_description = "List of muted inputs"
    breadcrumb = ["Muted Inputs"]


class CreateMutedInput(LoginRequiredMixin, PageTitleMixin, generic.CreateView):
    """CreateMutedInput: CreateView than
    create a new MutedInput object in DB"""
    form_class = MutedInputForm
    page_header = "New Muted Input"
    page_header_description = ""
    breadcrumb = ["Muted Inputs", "New Muted Input"]
    success_url = reverse_lazy('measurements:measurement_front:list-muted-input')
    template_name = 'create_muted.html'

    def form_valid(self, form):

        muted = form.save()

        if muted:
            msg = 'Se ha creado el muted input'
            messages.success(self.request, msg)
        else:
            msg = 'No se pudo crear el muted input'
            messages.error(self.request, msg)

        return HttpResponseRedirect(self.success_url)


class DetailMutedInput(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    """DetailMutedInput: DetailView than
    give the details of a specific MutedInput object"""
    model = MutedInput
    context_object_name = "mute"
    template_name = "detail_muted.html"
    page_header = "Muted Input Details"
    page_header_description = ""
    breadcrumb = ["Muted Inputs", "Muted Input Details"]


class DeleteMutedInput(LoginRequiredMixin, generic.DeleteView):
    """DeleteMutedInput: DeleteView than delete an specific muted input."""
    model = MutedInput
    success_url = reverse_lazy('measurements:measurement_front:list-muted-input')


class UpdateMutedInput(LoginRequiredMixin, PageTitleMixin, generic.UpdateView):
    """UpdateMutedInput: UpdateView than
    update an MutedInput object in DB"""
    form_class = MutedInputForm
    context_object_name = 'muted'
    page_header = "Update Muted Input"
    page_header_description = ""
    breadcrumb = ["Muted Inputs", "Edit Muted Input"]
    model = MutedInput
    success_url = reverse_lazy('measurements:measurement_front:list-muted-input')
    template_name = 'create_muted.html'

    def get_context_data(self, **kwargs):

        context = super(UpdateMutedInput, self).get_context_data(**kwargs)
        muted = self.get_object()
        form = self.get_form_class()

        # Initial data for the form
        context['form'] = form(initial={'url': muted.url,
                                        'type_med': muted.type_med
                                        })

        return context

    def form_valid(self, form):

        muted = form.save()

        if muted:
            msg = 'Se ha editado el muted input'
            messages.success(self.request, msg)
        else:
            msg = 'No se pudo editar el muted input'
            messages.error(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


# Probe CRUD


class ListProbe(PageTitleMixin, generic.ListView):
    """ListProbe: ListView than
    display a list of all probe"""
    model = Probe
    template_name = "list_probe.html"
    context_object_name = "probes"
    page_header = "Probes"
    page_header_description = "List of Probes"
    breadcrumb = ["Probes"]


class CreateProbe(PageTitleMixin, generic.CreateView):
    """CreateProbe: CreateView than
    create a new Probe object in DB"""
    form_class = ProbeForm
    page_header = "New Probe"
    page_header_description = ""
    breadcrumb = ["Probes", "New Probe"]
    success_url = reverse_lazy('measurements:measurement_front:list-probe')
    template_name = 'create_probe.html'

    def form_valid(self, form):

        probe = form.save()

        if probe:
            msg = 'Se ha creado la sonda'
            messages.success(self.request, msg)
        else:
            msg = 'No se pudo crear la sonda'
            messages.error(self.request, msg)

        return HttpResponseRedirect(self.success_url)


class CreateProbeAjax(LoginRequiredMixin, generic.View):
    http_method_names = [u'get', ]
    id = None

    def get(self, request, *args, **kwargs):

        self.id = request.GET['id']

        if request.GET['country'] == 'true':
            data = self.country()
        else:
            data = self.isp()

        return JsonResponse({'data': data})

    def country(self):
        country = Country.objects.get(id=self.id)
        states = State.objects.filter(country=country)
        full_states = []
        for state in states:
            node = {'id': state.id, 'text': state.name}
            full_states.append(node)
        return full_states

    def isp(self):
        isp = ISP.objects.get(id=self.id)
        plans = Plan.objects.filter(isp=isp)
        full_plans = []
        for plan in plans:
            node = {'id': plan.id, 'text': plan.name}
            full_plans.append(node)
        return full_plans


class DetailProbe(PageTitleMixin, generic.DetailView):
    """DetailProbe: DetailView than
    give the details of a specific Probe object"""
    model = Probe
    slug_url_kwarg = 'identification'
    slug_field = 'identification'
    context_object_name = "probe"
    template_name = "detail_probe.html"
    page_header = "Probe Details"
    page_header_description = ""
    breadcrumb = ["Probes", "Probe Details"]


class DeleteProbe(generic.DeleteView):
    """DeleteProbe: DeleteView for deleting a specific probe."""
    model = Probe
    slug_url_kwarg = 'identification'
    slug_field = 'identification'
    success_url = reverse_lazy('measurements:measurement_front:list-probe')


class UpdateProbe(PageTitleMixin, generic.UpdateView):
    """UpdateProbe: UpdateView for
    updating a Probe object in DB"""
    form_class = ProbeForm
    context_object_name = 'probe'
    page_header = "Update Probe"
    page_header_description = ""
    breadcrumb = ["Probes", "Edit Probe"]
    model = Probe
    slug_url_kwarg = 'identification'
    slug_field = 'identification'
    success_url = reverse_lazy('measurements:measurement_front:list-probe')
    template_name = 'create_probe.html'

    def get_context_data(self, **kwargs):

        context = super(UpdateProbe, self).get_context_data(**kwargs)
        probe = self.get_object()
        form = self.get_form_class()

        # Initial data for the form
        context['form'] = form(initial={'identification': probe.identification,
                                        'region': probe.region,
                                        'country': probe.country,
                                        'city': probe.city,
                                        'isp': probe.isp,
                                        'plan': probe.plan
                                        })
        return context

    def form_valid(self, form):

        probe = form.save()

        if probe:
            msg = 'Se ha editado la sonda'
            messages.success(self.request, msg)
        else:
            msg = 'No se pudo editar la sonda'
            messages.error(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


# Report Views


class ListReportView(PageTitleMixin, generic.ListView):
    """ListReportView: ListView than
    display a list of all reports"""
    queryset = Metric.objects.all().values('report_id').distinct()
    template_name = "list_report.html"
    context_object_name = "reports"
    page_header = "Reports"
    page_header_description = "List of Reports"
    breadcrumb = ["Reports"]


class DetailReportView(PageTitleMixin, generic.DetailView):
    """DetailReportView: DetailView than
    give the details of a specific Report"""
    model = Metric
    context_object_name = "report"
    template_name = "detail_report.html"
    page_header = "Report Details"
    page_header_description = ""
    breadcrumb = ["Reports", "Report Details"]
    slug_url_kwarg = 'report_id'
    slug_field = 'report_id'

    def get(self, request, *args, **kwargs):
        self.object = self.kwargs['report_id']
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(DetailReportView, self).get_context_data(**kwargs)
        metrics = Metric.objects.filter(
            report_id=self.kwargs['report_id'])
        context['metrics'] = metrics.values(
            'id', 'measurement', 'input', 'annotations')
        report = metrics.first()
        context['report'] = report
        return context


class ListReportProbeView(ListReportView):
    """ListReportProbeView: ListView extends of ListReportView than
    display a list of all reports of a specific probe"""
    def get_queryset(self):
        probe_id = self.kwargs['pk']
        queryset = Metric.objects.annotate(
            val=RawSQL("annotations->>'probe'", ())).filter(
            val=probe_id).values('report_id').distinct()
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ListReportProbeView, self).get_context_data(**kwargs)
        context['probe_id'] = self.kwargs['pk']
        return context


# Manual Flags View


class ManualFlagsView(generic.FormView):
    """
    ManualFlagsView: CreateView for create manual flags
    in DB
    """
    form_class = ManualFlagForm
    success_url = reverse_lazy('measurements:measurement_front:measurement-table')
    template_name = 'display_table.html'

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # Get metrics values
        metric_inputs = form.cleaned_data['metrics']

        if metric_inputs.endswith(','):
            metric_inputs = metric_inputs[:-1]

        print metric_inputs

        # Create database object #
        database = DBconnection('titan_db')
        query = "select id, input, measurement_start_time, test_name, annotations "
        query += "from metrics where id in (" + metric_inputs + ")"

        # Results from execute queries #
        metrics = database.db_execute(query)

        if metrics:
            rows_ids = metrics['rows']

            # For each values in rows_ids
            for row in rows_ids:
                # Change or create flag to Manual Flag
                change_to_manual_flag_sql(row)

        msg = 'Se han agregado los flags manuales'
        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())

        # q = Metric.objects.first()

# Create Events From Measurements


class EventFromMeasurementView(PageTitleMixin, generic.FormView):
    """
    EventFromMeasurementView: FormView for create event from measurements
    """
    page_header = "Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurements", "All"]
    form_class = ManualFlagForm
    success_url = ""
    template_name = 'display_table.html'
    measurement_type = 'MED'

    def get_success_url(self, id):
        return reverse_lazy(
            'events:event_front:create-event-from-measurements',
            kwargs={'pk': id})

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # Get metrics values
        metric_inputs = form.cleaned_data['metrics']
        error_msg = ""

        if metric_inputs.endswith(','):
            metric_inputs = metric_inputs[:-1]

        # Create database object #
        try:
            database = DBconnection('titan_db')

            query = "select id, input, measurement_start_time, test_name, annotations "
            query += "from metrics where id in (" + metric_inputs + ")"
            # Results from execute queries #
            metrics = database.db_execute(query)
        except Exception:
            error_msg = "Database connection error"
        if metrics:
            rows_ids = metrics['rows']
            validation = validate_metrics(rows_ids)
            if validation is True:

                # Change or create flag to Manual Flag
                event = change_to_manual_flag_and_create_event(
                    rows_ids,
                    self.measurement_type
                )
                if event is not False:
                    msg = 'New event created'
                    messages.success(self.request, msg)

                    return HttpResponseRedirect(self.get_success_url(event.id))
            elif validation == "no probe":
                error_msg = "Measurements must have a probe in annotations. "
            elif validation == "no same input or test_name":
                error_msg = "Measurements must have the same Input and Test Name. "
            elif validation == "already in event":
                error_msg = "One measurement have already an event"

        msg = 'Error creating new Event. ' + error_msg
        messages.error(self.request, msg)
        return self.form_invalid(form)


class EventFromDNSMeasurementView(EventFromMeasurementView, DNSTableView):
    """EventFromMeasurementView: EventFromMeasurementView extention
    for create event from DNS measurements in DB"""
    page_header = "DNS Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurements", "DNS"]
    form_class = MeasurementToEventForm
    template_name = 'list_dns.html'
    measurement_type = 'DNS'

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # Get metrics values
        error_msg = ""
        metric_inputs = form.cleaned_data['metrics']
        metric_ips = form.cleaned_data['metric_ip']

        if metric_inputs.endswith(','):
            metric_inputs = metric_inputs[:-1]

        if metric_ips.endswith(','):
            metric_ips = metric_ips[:-1]

        # list_metric_ips = metric_ips.split(',')

        # Create database object #
        try:
            database = DBconnection('titan_db')

            query = "select id, input, measurement_start_time, test_name, annotations "
            query += "from metrics where id in (" + metric_inputs + ")"
            # Results from execute queries #
            metrics = database.db_execute(query)
        except Exception:
            error_msg = "Database connection error"
        if metrics:
            rows_ids = metrics['rows']
            validation = validate_metrics(rows_ids)
            if validation is True:

                # Change or create flag to Manual Flag
                event = change_to_flag_and_create_event(
                    rows_ids,
                    metric_ips,
                    self.measurement_type
                )
                if event is not False:
                    msg = 'New event created'
                    messages.success(self.request, msg)

                    return HttpResponseRedirect(self.get_success_url(event.id))
            elif validation == "no probe":
                error_msg = "Measurements must have a probe in annotations. "
            elif validation == "no same input or test_name":
                error_msg = "Measurements must have the same Input and Test Name. "
            elif validation == "already in event":
                error_msg = "One measurement have already an event"

        msg = 'Error creating new Event. ' + error_msg
        messages.error(self.request, msg)
        return self.form_invalid(form)


class EventFromTCPMeasurementView(EventFromMeasurementView):
    """EventFromMeasurementView: EventFromMeasurementView extention
    for create event from TCP measurements in DB"""
    page_header = "TCP Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurements", "TCP"]
    form_class = MeasurementToEventForm
    template_name = 'display_tcp_table.html'
    measurement_type = 'TCP'

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # Get metrics values
        error_msg = ""
        metric_inputs = form.cleaned_data['metrics']
        metric_ips = form.cleaned_data['metric_ip']

        if metric_inputs.endswith(','):
            metric_inputs = metric_inputs[:-1]

        if metric_ips.endswith(','):
            metric_ips = metric_ips[:-1]

        # list_metric_ips = metric_ips.split(',')

        # Create database object #
        try:
            database = DBconnection('titan_db')

            query = "select id, input, measurement_start_time, test_name, annotations "
            query += "from metrics where id in (" + metric_inputs + ")"
            # Results from execute queries #
            metrics = database.db_execute(query)
        except Exception:
            error_msg = "Database connection error"
        if metrics:
            rows_ids = metrics['rows']
            validation = validate_metrics(rows_ids)
            if validation is True:

                # Change or create flag to Manual Flag
                event = change_to_flag_and_create_event(
                    rows_ids,
                    metric_ips,
                    self.measurement_type
                )
                if event is not False:
                    msg = 'New event created'
                    messages.success(self.request, msg)

                    return HttpResponseRedirect(self.get_success_url(event.id))
            elif validation == "no probe":
                error_msg = "Measurements must have a probe in annotations. "
            elif validation == "no same input or test_name":
                error_msg = "Measurements must have the same Input and Test Name. "
            elif validation == "already in event":
                error_msg = "One measurement have already an event"

        msg = 'Error creating new Event. ' + error_msg
        messages.error(self.request, msg)
        return self.form_invalid(form)


class EventFromHTTPMeasurementView(EventFromMeasurementView):
    """EventFromMeasurementView: EventFromMeasurementView extention
    for create event from HTTP measurements in DB"""
    page_header = "HTTP Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurements", "HTTP"]
    form_class = ManualFlagForm
    template_name = 'display_http_table.html'
    measurement_type = 'HTTP'


class CreateManualFlag(generic.View):

    flag_id = None
    object = None

    def post(self, request, *args, **kwargs):

            self.flag_id = request.POST['flag']
            self.object = Flag.objects.get(uuid=self.flag_id)
            self.object.flag = Flag.HARD
            self.object.manual_flag = True
            self.object.save()
            suggestedEvents(self.object)

            return JsonResponse({'data': True})

######################## PRUEBA #######################################


class PruebaDataTable(generic.TemplateView):

    template_name = 'list.html'


class PruebaDataTableAjax(DatatablesView):

    fields = ('id', 'toto')
    queryset = Metric.objects.annotate(
        toto=RawSQL(
            "test_keys->>'failures'", ()
        )
    ).all()

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )

    def get(self, request, *args, **kwargs):
        email = EmailMessage('title', 'body', to=['nestorbracho2207@gmail.com'])
        email.send()
