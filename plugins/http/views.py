from plugins.views import PluginTableView
from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from plugins.http.models import HTTP
import json


class HTTPTableView(PluginTableView):
    page_header = "HTTP Measurement List"
    page_header_description = ""
    breadcrumb = ["Measurement", "HTTP"]
    titles = [
        'checkbox',
        'flag',
        'manual_flag',
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
    fields = {
        'checkbox': 'metric__input',
        'flag': 'flag__is_flag',
        'manual flag': 'flag__manual_flag',
        'status code match': 'status_code_match',
        'headers match': 'headers_match',
        'body lenght match': 'body_length_match',
        'body proportion': 'body_proportion',
        'test keys': 'metric__test_keys',
        'measurement': 'metric__measurement',
        'input': 'metric__input',
        'measurement_start_time': 'metric__measurement_start_time',
        'report_id': 'metric__report_id',
        'probe id': 'metric__probe__identification',
        'probe ISP': 'metric__probe__isp'

    }

    queryset = HTTP.objects.all().select_related('metric__probe', 'flag')

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )
