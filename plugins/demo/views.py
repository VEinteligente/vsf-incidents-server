from plugins.views import PluginTableView
from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.expressions import RawSQL


from measurement.models import Metric
import json


class DemoTableView(PluginTableView):
    page_header = "DEMO Measurement List"
    page_header_description = "Demo example"
    breadcrumb = ["Measurement", "DEMO"]
    titles = ['flags', 'id', 'input', 'queries']
    url_ajax = '/plugins/demo/demo-ajax/'


class DemoAjaxView(DatatablesView):
    fields = {
        'flags': 'flags__flag',
        'id': 'id',
        'input': 'input',
        'queries': 'queries'
    }
    queryset = Metric.objects.all().annotate(
        queries=RawSQL(
            "test_keys->>'queries'", ()
        )
    )

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )


def hola_hola():
    print 'esto es una prueba exitosa'
    return True


def chao_chao():
    print "WOOOOOOOOOOOOOOHOOOOOOOOOOOOOOO------------"
    return False

