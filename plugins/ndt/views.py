import json
from plugins.views import PluginTableView
from eztables.views import DatatablesView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.expressions import RawSQL

from django.views import generic
from datetime import datetime
from measurement.models import Metric, Probe
from models import DayTest
# from measurement.models import Country, State, Probe
# import random


class DemoTableView(PluginTableView):
    page_header = "DEMO Measurement List"
    page_header_description = "Demo example"
    breadcrumb = ["Measurement", "NDT"]
    titles = ['flags', 'id', 'input', 'queries']
    url_ajax = '/plugins/demo/demo-ajax/'


class NdtAjaxView(DatatablesView):
    fields = {
        'id': 'id',
        'annotations': 'annotations',
        'probe': 'queries'
    }
    queryset = Metric.objects.filter(test_name='ndt').annotate(
        queries=RawSQL(
            "test_keys->>'queries'", ()
        )
    )

    def get_rows(self, rows):
        return super(NdtAjaxView, self).get_rows(rows)

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )

# --------------------------------------------------------


class PuraPrueba(generic.TemplateView):

    template_name = 'table.html'

    def get(self, request, *args, **kwargs):

        # ----------- Create 200 random probes!

        # isp = ['Cantv', 'Digitel', 'Movistar', 'Inter']
        # country = Country.objects.get(name='Venezuela')
        # for i in range(1000, 1200):
        #     state = State.objects.filter(country=country).order_by('?').first()
        #     p = Probe(
        #         identification=i,
        #         region=state,
        #         country=country,
        #         city='Generic City',
        #         isp=random.choice(isp)
        #     )
        #     try:
        #         p.save()
        #     finally:
        #         print(i)

        # -------------------------------------

        metric = Metric.objects.filter(test_name='ndt').order_by('test_start_time').first()
        print(metric.test_start_time)
        print(metric.annotations['probe'])
        print(datetime(year=2017, month=2, day=10))
        probe = Probe.objects.get(identification='1002')
        dt = DayTest(
            probe=probe,
            date=datetime(year=2017, month=2, day=10)
        )
        dt.save()
        return super(PuraPrueba, self).get(args, kwargs)
