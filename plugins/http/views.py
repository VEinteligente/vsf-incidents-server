from plugins.views import PluginUpdateEventView, PluginCreateEventView
from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from plugins.http.models import HTTP
import json


class HTTPTableView(PluginCreateEventView):
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
        'measurement',
        'input',
        'test name',
        'measurement_start_time',
        'status code match',
        'headers match',
        'body lenght match',
        'body proportion',
        'report_id',
        'probe id',
        'test keys'
    ]
    url_ajax = '/plugins/http/http-ajax/'
    enable_event = True


class HTTPUpdateEventView(PluginUpdateEventView):
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
        'measurement',
        'input',
        'test name',
        'measurement_start_time',
        'status code match',
        'headers match',
        'body lenght match',
        'body proportion',
        'report_id',
        'probe id',
        'test keys'
    ]
    url_ajax = '/plugins/http/http-ajax/'
    enable_event = True



class HTTPAjaxView(DatatablesView):
    """
    HTTPAjaxView: DatatablesView for fill http metrics table.
    Field checkbox is required to do functions over the table and must be
    the id to identify which metric is selected.
    Field measurement_id is required if measurement field is present
    Field checkbox, flag, test_keys, measurement, report_id are customized by
    table.html
    """
    fields = {
        'checkbox': 'flag__uuid',  # Required
        'flag': 'flag__flag',  # Customized
        'test name': 'metric__test_name',
        'manual flag': 'flag__manual_flag',
        'status code match': 'status_code_match',
        'headers match': 'headers_match',
        'body lenght match': 'body_length_match',
        'body proportion': 'body_proportion',
        'test keys': 'metric__test_keys',  # Customized
        'measurement': 'metric__measurement',  # Customized
        'measurement_id': 'metric__id',  # Required for measurement
        'input': 'metric__input',
        'measurement_start_time': 'metric__measurement_start_time',
        'report_id': 'metric__report_id',  # Customized
        'probe id': 'metric__probe__identification'
    }

    queryset = HTTP.objects.all().select_related('metric__probe', 'flag')

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )
