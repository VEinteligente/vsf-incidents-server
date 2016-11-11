from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.serializers.json import DjangoJSONEncoder
from django.views import generic
from django.db import connections
from django.db.models import Q
from eztables.views import DatatablesView
from django.utils.six import text_type
from measurement.models import DNS, Flag, Metric
import re
import json

from dashboard.mixins import PageTitleMixin

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

        Args:
            query (str): SQL query

        Returns:
            dict: A dictionary with data for columns and rows
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

    def get_isp_sonda(self):
        """Get probe's ISP value in Test key object
        Returns:
            string: probe's ISP value
        """
        if self.annotations:
            return self.annotations['isp']

    def get_tcp_connect(self):
        """Get TCP connections list in Test key object
        Returns:
            list: list of TCP connections
        """
        if self.tcp_connect:
            return self.tcp_connect
        else:
            return []

    def ignore_data(self, list_public_dns=None):
        """Filter every object with probe ISP in list
        Args:
            list_public_dns: List of public DNS to ignore
        """
        try:
            sonda_isp = self.get_isp_sonda()

            # Find ip list #
            # from sonda_isp provider #
            # Output: ip list #
            ips_required = [dns.ip
                            for dns in
                            DNS.objects.filter(Q(isp=sonda_isp) |
                                               Q(isp='digitel'))]

            # Leave only ips from ips_required list #
            self.left_data_from_list(ips_required)

            # Ignore ips registered as public access #
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
        self.failed = [ip for ip in self.failed
                       if self.failed and ip not in list_ip]

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
        self.failed = [ip for ip in self.failed
                       if self.failed and ip in list_ip]

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


class MeasurementTableView(PageTitleMixin, generic.TemplateView):
    """MeasurementTableView: TemplateView than
    display a list of all metrics in DB"""

    page_header = "Measurement List"
    page_header_description = ""
    breadcrumb = [""]
    template_name = 'display_table.html'

    def get_context_data(self, **kwargs):

        context = super(MeasurementTableView, self).get_context_data(**kwargs)

        # Create database object #
        database = DBconnection('titan_db')
        query = "select * from metrics where test_name='web_connectivity' LIMIT 10"

        result = database.db_execute(query)
        context['rows'] = {}
        context['columns'] = {}

        if result:
            # Search every metric with flag in DB
            flags = Flag.objects.all().values('medicion', 'flag')
            # Add Column Flag and his value in every row in Rows dictionary
            result['columns'].insert(0, "flag")
            for row in result['rows']:
                flag_value = "not"
                for flag in flags:
                    if (str(flag['medicion']) == str(row['id'])):
                        flag_value = flag['flag']
                row.update({'flag': flag_value})
            context['rows'] = result['rows']
            context['columns'] = result['columns']

        return context


class DNSTableView(generic.TemplateView):
    """DNSTableView: TemplateView than
    display a list of metrics in DB
    with dns_consistency as test_name"""

    template_name = 'display_dns_table.html'

    def get_context_data(self, **kwargs):

        context = super(DNSTableView, self).get_context_data(**kwargs)

        try:

            # Create database object #
            database = DBconnection('titan_db')
            query = "select id, input, test_keys, measurement_start_time "
            query += "from metrics where test_name='dns_consistency' "

            result = database.db_execute(query)
            rows = {}
            columns = {}

            if result:

                rows = result['rows']
                columns = result['columns']

            # Adding columns
            columns_final = ['flag'] + columns[:len(columns) / 2]
            columns_final += ['match', 'dns isp',
                              'control result',
                              'dns name', 'dns result']
            columns_final += columns[len(columns) / 2:]
            columns_final.remove('test_keys')

            # Answers
            ans = self.get_answers(rows)

            # Context data variables #
            context['rows'] = [dict(zip(columns_final, row)) for row in ans]
            context['columns'] = columns_final

        except Exception as e:
            print e

        return context

    def get_answers(self, rows):
        """ Create from every row a Test Key object to
        extract the data to display in the list
        Args:
            rows: DB rows
        """

        ans = []

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))

            # Get sonda isp and public DNS #
            dns_isp = test_key.get_isp_sonda()
            public_dns = [dns.ip
                          for dns in DNS.objects.filter(public=True)]

            # Ignore data from test_key #
            if test_key.ignore_data(public_dns):

                # Get queries #
                queries = test_key.get_queries()

                if not queries[0]['failure']:

                    # Get answers #
                    answers = queries[0]['answers']

                    # Get control resolver from answer_type A #
                    for a in answers:
                        if a['answer_type'] == 'A':
                            control_resolver = a['ipv4']

                    # Verify each result from queries with control resolver #
                    for query in queries:

                        dns_name = query['resolver_hostname']
                        match = False
                        flag_status = 'No flag'

                        # If query has failure, dns result #
                        # is a failure response and match is False #

                        # If query doesn't has failure, then find dns result #
                        # from answer type A and later compare it with control #
                        # resolver. If both are the same, match is True otherwise #
                        # match is False #

                        if query['failure']:
                            dns_result = query['failure']

                        answers = query['answers']

                        for a in answers:
                            if a['answer_type'] == 'A':
                                dns_result = a['ipv4']

                        if control_resolver == dns_result:
                            match = True
                        else:
                            # Search flag #

                            if Flag.objects.filter(ip=dns_name,
                                                   medicion=row['id'],
                                                   type_med='DNS').exists():

                                f = Flag.objects.get(ip=dns_name,
                                                     medicion=row['id'],
                                                     type_med='DNS')

                                if f.flag:
                                    flag_status = 'hard'
                                elif f.flag is False:
                                    flag_status = 'soft'
                                elif f.flag is None:
                                    flag_status = 'muted'

                        # If dns_name is in DNS table, find its name #
                        if DNS.objects.filter(ip=dns_name).exists():
                            dns_table_name = DNS.objects\
                                                .get(ip=dns_name).verbose
                        else:
                            dns_table_name = dns_name

                        # Formating the answers #
                        ans += [[flag_status, row['id'], row['input'],
                                match, dns_isp, control_resolver,
                                dns_table_name, dns_result,
                                row['measurement_start_time']]]

        return ans


class TCPTableView(generic.TemplateView):
    """TCPTableView: TemplateView than
    display a list of metrics in DB
    with web_connectivity as test_name"""

    template_name = 'display_dns_table.html'

    def get_context_data(self, **kwargs):

        context = super(TCPTableView, self).get_context_data(**kwargs)

        try:
            # Create database connection #
            database = DBconnection('titan_db')
            query = "select id, input, test_keys, probe_cc, probe_ip, "
            query += "measurement_start_time "
            query += "from metrics where test_name='web_connectivity' "

            result = database.db_execute(query)

            rows = {}
            columns = {}

            if result:

                rows = result['rows']
                columns = result['columns']

            # Adding columns
            columns_final = ['flag'] + columns[:len(columns) / 2]
            columns_final += ['ip', 'port', 'bloqueado', 'medicion exitosa']
            columns_final += columns[len(columns) / 2:]
            columns_final.remove('test_keys')

            # Answers #
            ans = self.get_answers(rows)

            # Context data variables #
            context['rows'] = [dict(zip(columns_final, row)) for row in ans]
            context['columns'] = columns_final

        except Exception as e:

            print e

        return context

    def get_answers(self, rows):
        """ Create from every row a Test Key object to
        extract the data to display in the list
        Args:
            rows: DB rows
        """
        ans = []

        for row in rows:

            # Convert json test_keys into python object
            test_key = DNSTestKey(json.dumps(row['test_keys']))
            tcp_connect = test_key.get_tcp_connect()

            for tcp in tcp_connect:

                flag_status = 'No flag'

                if Flag.objects.filter(ip=tcp['ip'],
                                       medicion=row['id'],
                                       type_med='TCP').exists():

                    f = Flag.objects.get(ip=tcp['ip'],
                                         medicion=row['id'],
                                         type_med='TCP')

                    if f.flag:
                        flag_status = 'hard'
                    elif f.flag is False:
                        flag_status = 'soft'
                    elif f.flag is None:
                        flag_status = 'muted'

                ip = tcp['ip']
                port = tcp['port']
                blocked = tcp['status']['blocked']
                success = tcp['status']['success']

                # Formating the answers #
                ans += [[flag_status, row['id'], row['input'],
                         ip, port, blocked, success,
                         row['probe_cc'], row['probe_ip'],
                         row['measurement_start_time']]]

        return ans


class HTTPTableView(generic.TemplateView):
    """HTTPTableView: TemplateView than
    display a list of metrics in DB using
    HTTPListDatatablesView"""

    template_name = 'display_http_table.html'


class HTTPListDatatablesView(DatatablesView):
    """HTTPListDatatablesView: DatatablesView than
    populate a DataTable with all metrics with web_connectivity
    as test_name"""

    model = Metric
    queryset = Metric.objects.filter(test_name='web_connectivity')
    fields = {
        'id': 'id',
        'measurement_start_time': 'measurement_start_time',
        'input': 'input',
        'probe_cc': 'probe_cc',
        'test': 'test_keys'
    }

    # def get_field(self, index):
    #     if isinstance(self.fields, dict):
    #         print index
    #         print self.fields
    #         print "---------------------------------------------------------------------------"
    #         print self.dt_data
    #         return self.dt_data['mDataProp_%s' % index]
    #     else:
    #         return self.fields[index]

    def get_row(self, row):
        '''Format a single row (if necessary)'''

        if isinstance(self.fields, dict):
            a = dict([
                (key, text_type(value).format(**row) if RE_FORMATTED.match(value) else row[value])
                for key, value in self.fields.items()
            ])

            if a['test']['body_length_match']:
                a['body_length_match'] = '<i class="fa fa-check" style="color: green;" aria-hidden="true"></i>' \
                                     '<span class="hide">Yes</span>'
            else:
                a['body_length_match'] = '<i class="fa fa-times" style="color: red;" aria-hidden="true"></i>' \
                                     '<span class="hide">No</span>'

            try:
                if a['test']['body_proportion']:
                    a['body_proportion'] = a['test']['body_proportion']
            except KeyError:
                a['body_proportion'] = 2

            if a['test']['headers_match']:
                a['headers_match'] = '<i class="fa fa-check" style="color: green;" aria-hidden="true"></i>' \
                                     '<span class="hide">Yes</span>'
            else:
                a['headers_match'] = '<i class="fa fa-times" style="color: red;" aria-hidden="true"></i>' \
                                     '<span class="hide">No</span>'

            if a['test']['status_code_match']:
                a['status_code_match'] = '<i class="fa fa-check" style="color: green;" aria-hidden="true"></i>' \
                                     '<span class="hide">Yes</span>'
            else:
                a['status_code_match'] = '<i class="fa fa-times" style="color: red;" aria-hidden="true"></i>' \
                                     '<span class="hide">No</span>'

            if a['test']['title_match']:
                a['title_match'] = '<i class="fa fa-check" style="color: green;" aria-hidden="true"></i>' \
                                     '<span class="hide">Yes</span>'
            else:
                a['title_match'] = '<i class="fa fa-times" style="color: red;" aria-hidden="true"></i>' \
                                     '<span class="hide">No</span>'

            return a
        else:
            return [text_type(field).format(**row) if RE_FORMATTED.match(field)
                    else row[field]
                    for field in self.fields]

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )


class PruebaDataTable(generic.TemplateView):

    template_name = 'list.html'

    def get(self, request, *args, **kwargs):
        print "done"

        return super(PruebaDataTable, self).get(request, *args, **kwargs)
