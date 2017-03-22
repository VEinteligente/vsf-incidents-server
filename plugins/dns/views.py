from plugins.views import PluginTableView
from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from plugins.dns.models import DNS
import json


class DNSTableView(PluginTableView):
    page_header = "DNS Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurement", "DNS"]
    titles = [
        'checkbox',
        'flag',
        'manual_flag',
        'control resolver failure',
        'control resolver answers',
        'control resolver hostname',
        'failure',
        'answers',
        'resolver hostname',
        'test keys',
        'measurement',
        'input',
        'measurement_start_time',
        'report_id',
        'probe id',
        'probe ISP'
    ]
    url_ajax = '/plugins/dns/dns-ajax/'


class DNSAjaxView(DatatablesView):
    fields = {
        'checkbox': 'metric__input',
        'flag': 'flag__is_flag',
        'manual flag': 'flag__manual_flag',
        'control resolver failure': 'control_resolver_failure',
        'control resolver answers': 'control_resolver_answer',
        'control resolver hostname': 'control_resolver_resolver_hostname',
        'failure': 'failure',
        'answers': 'answer',
        'resolver hostname': 'resolver_hostname',
        'test keys': 'metric__test_keys',
        'measurement': 'metric__measurement',
        'input': 'metric__input',
        'measurement_start_time': 'metric__measurement_start_time',
        'report_id': 'metric__report_id',
        'probe id': 'metric__probe__identification',
        'probe ISP': 'metric__probe__isp'

    }

    queryset = DNS.objects.all().select_related('metric__probe', 'flag')

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )
