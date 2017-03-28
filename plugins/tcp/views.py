from plugins.views import PluginTableView
from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from plugins.tcp.models import TCP
import json


class TCPTableView(PluginTableView):
    """
    TCPTableView: PluginTableView for display tcp metrics table.
    Field checkbox is obligatory to do functions over the table
    """
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
    """
    TCPAjaxView: DatatablesView for fill tcp metrics table.
    Field checkbox is required to do functions over the table and must be
    the id to identify which metric is selected.
    Field measurement_id is required if measurement field is present
    Fields flag and is_flag are required to display Flag header defined in
    TCPTableView.
    Field checkbox, flag, test_keys, measurement, report_id are customized by
    table.html
    """
    fields = {
        'checkbox': 'id',  # Required
        'flag': 'flag__flag',  # Customized
        'is_flag': 'flag__is_flag',
        'test name': 'metric__test_name',
        'manual flag': 'flag__manual_flag',
        'status blocked': 'status_blocked',
        'status failure': 'status_failure',
        'status success': 'status_success',
        'test keys': 'metric__test_keys',  # Customized
        'measurement': 'metric__measurement',  # Customized
        'measurement_id': 'metric__id',  # Required for measurement
        'input': 'metric__input',
        'measurement_start_time': 'metric__measurement_start_time',
        'report_id': 'metric__report_id',  # Customized
        'probe id': 'metric__probe__identification',
        'probe ISP': 'metric__probe__isp'

    }

    queryset = TCP.objects.all().select_related('metric__probe', 'flag')

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )
