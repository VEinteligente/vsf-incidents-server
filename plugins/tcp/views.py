from plugins.views import PluginTableView
from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from plugins.tcp.models import TCP
import json


class TCPTableView(PluginTableView):
    page_header = "TCP Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurement", "TCP"]
    titles = [
        'checkbox',
        'flag',
        'manual flag',
        'test name',
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
    url_ajax = '/plugins/tcp/tcp-ajax/'


class TCPAjaxView(DatatablesView):
    fields = {
        'checkbox': 'metric__id',
        'flag': 'flag__flag',
        'is_flag': 'flag__is_flag',
        'test name': 'metric__test_name',
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
        'probe ISP': 'metric__probe__isp'

    }

    queryset = TCP.objects.all().select_related('metric__probe', 'flag')

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )
