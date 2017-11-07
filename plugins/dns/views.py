from plugins.views import PluginUpdateEventView, PluginCreateEventView, DatatablesView
# from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from cgi import escape

from plugins.dns.models import DNS
import json


class DNSTableView(PluginCreateEventView):
    """
    DNSTableView: PluginTableView for display dns metrics table.
    Field checkbox is obligatory to do functions over the table
    """
    page_header = "DNS Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurement", "DNS"]
    titles = [
        'checkbox',
        'flag',
        'manual flag',
        'measurement',
        'isp',
        'input',
        'site',
        'category',
        'test name',
        'measurement_start_time',
        'region',
        'control resolver failure',
        'control resolver answers',
        'control resolver hostname',
        'failure',
        'answers',
        'resolver hostname',
        'report_id',
        'probe id',
        'test keys'
    ]
    url_ajax = '/plugins/dns/dns-ajax/'
    enable_event = True


class DNSUpdateEventView(PluginUpdateEventView):
    """
    DNSTableView: PluginTableView for display dns metrics table.
    Field checkbox is obligatory to do functions over the table
    """
    page_header = "DNS Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurement", "DNS"]
    titles = [
        'checkbox',
        'flag',
        'manual flag',
        'measurement',
        'isp'
        'input',
        'site',
        'category',
        'test name',
        'measurement_start_time',
        'region',
        'control resolver failure',
        'control resolver answers',
        'control resolver hostname',
        'failure',
        'answers',
        'resolver hostname',
        'report_id',
        'probe id',
        'test keys'
    ]
    url_ajax = '/plugins/dns/dns-ajax/'
    enable_event = True


class DNSAjaxView(DatatablesView):
    """
    DNSAjaxView: DatatablesView for fill dns metrics table.
    Field checkbox is required to do functions over the table and must be
    the id to identify which metric is selected.
    Field measurement_id is required if measurement field is present
    Field checkbox, flag, test_keys, measurement, report_id,
    control_resolver_answers and answers are customized by
    table.html
    """
    fields = {
        'checkbox': 'flag__uuid',  # Required
        'flag': 'flag__flag',  # Customized
        'manual flag': 'flag__manual_flag',
        'test name': 'metric__test_name',
        'isp': 'flag__isp__name',
        'control resolver failure': 'control_resolver_failure',
        'control resolver answers': 'control_resolver_answers',  # Customized
        'control resolver hostname': 'control_resolver_resolver_hostname',
        'region': 'metric__probe__region__name',
        'failure': 'failure',
        'answers': 'answers',  # Customized
        'resolver hostname': 'resolver_hostname',
        'test keys': 'metric__test_keys',  # Customized
        'measurement': 'metric__measurement',  # Customized
        'measurement_id': 'metric__id',  # Required for measurement
        'input': 'metric__input',
        'site': 'flag__target__site__name',
        'category': 'flag__target__site__category',
        'measurement_start_time': 'metric__measurement_start_time',
        'report_id': 'metric__report_id',  # Customized
        'probe id': 'metric__probe__identification'

    }

    queryset = DNS.objects.all().select_related('metric__probe', 'flag')

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )

    def get_rows(self, rows):
        """
        Format all rows, and format % of package loss
        :param rows: All rows
        :return: dataTable page formatted
        """
        page_rows = super(DNSAjaxView, self).get_rows(rows)
        for row in page_rows:
            try:
                row['test keys'] = escape(str(row['test keys']))
            except TypeError:
                row['test name'] = 'Unknown'

        return page_rows
