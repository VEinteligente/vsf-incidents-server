from plugins.views import PluginTableView
from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from plugins.dns.models import DNS
import json


class DNSTableView(PluginTableView):
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
        'input',
        'test name',
        'measurement_start_time',
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
        'checkbox': 'id',  # Required
        'flag': 'flag__flag',  # Customized
        'manual flag': 'flag__manual_flag',
        'test name': 'metric__test_name',
        'control resolver failure': 'control_resolver_failure',
        'control resolver answers': 'control_resolver_answers',  # Customized
        'control resolver hostname': 'control_resolver_resolver_hostname',
        'failure': 'failure',
        'answers': 'answers',  # Customized
        'resolver hostname': 'resolver_hostname',
        'test keys': 'metric__test_keys',  # Customized
        'measurement': 'metric__measurement',  # Customized
        'measurement_id': 'metric__id',  # Required for measurement
        'input': 'metric__input',
        'measurement_start_time': 'metric__measurement_start_time',
        'report_id': 'metric__report_id',  # Customized
        'probe id': 'metric__probe__identification'

    }

    queryset = DNS.objects.all().select_related('metric__probe', 'flag')

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )
