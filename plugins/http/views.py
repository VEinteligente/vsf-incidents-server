from plugins.views import PluginTableView
from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from plugins.http.models import HTTP
import json


class HTTPTableView(PluginTableView):
    """
    HTTPTableView: PluginTableView for display http metrics table.
    Field checkbox is obligatory to do functions over the table
    """
    page_header = "HTTP Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurement", "HTTP"]
    titles = [
        'checkbox',
        'flag',
        'manual flag',
        'test name',
        'status code match',
        'headers match',
        'body lenght match',
        'body proportion',
        'test keys',
        'measurement',
        'input',
        'measurement_start_time',
        'report_id',
        'probe id',
        'probe ISP'
    ]
    url_ajax = '/plugins/http/http-ajax/'


class HTTPAjaxView(DatatablesView):
    """
    HTTPAjaxView: DatatablesView for fill http metrics table.
    Field checkbox is required to do functions over the table and must be
    the id to identify which metric is selected.
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
        'status code match': 'status_code_match',
        'headers match': 'headers_match',
        'body lenght match': 'body_length_match',
        'body proportion': 'body_proportion',
        'test keys': 'metric__test_keys',  # Customized
        'measurement': 'metric__measurement',  # Customized
        'input': 'metric__input',
        'measurement_start_time': 'metric__measurement_start_time',
        'report_id': 'metric__report_id',  # Customized
        'probe id': 'metric__probe__identification',
        'probe ISP': 'metric__probe__isp'

    }

    queryset = HTTP.objects.all().select_related('metric__probe', 'flag')

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )
