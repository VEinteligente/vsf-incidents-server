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


class NdtTableView(PluginTableView):
    page_header = "NDT Measurement List"
    page_header_description = "All NDT measurements"
    breadcrumb = ["Measurement", "NDT"]
    titles = [
        'annotations',
        'probe',
        'probe isp',
        'probe plan',
        'date',
        'report',
        'download',
        'upload',
        'ping',
        'max ping',
        'min ping',
        'time out',
        '% package loss',
    ]
    url_ajax = '/plugins/ndt/ndt-ajax/'


class NdtAjaxView(DatatablesView):
    fields = {
        'annotations': 'annotations',
        'probe': 'probe_uu',
        'probe_isp': 'id',
        'probe_plan': 'id',
        'date': 'test_start_time',
        'id': 'id',
        'report': 'report_id',
        'upload': 'upload',
        'download': 'download',
        'ping': 'ping',
        'min ping': 'min_ping',
        'max ping': 'max_ping',
        'time out': 'time_out',
        '% package loss': 'package_loss',
    }
    queryset = Metric.objects.filter(test_name='ndt').annotate(
        probe_uu=RawSQL(
            "annotations->>'probe'", ()
        ),
        download=RawSQL(
            "test_keys->'simple'->'download'", ()
        ),
        upload=RawSQL(
            "test_keys->'simple'->'upload'", ()
        ),
        ping=RawSQL(
            "test_keys->'simple'->'ping'", ()
        ),
        min_ping=RawSQL(
            "test_keys->'advanced'->'min_rtt'", ()
        ),
        max_ping=RawSQL(
            "test_keys->'advanced'->'max_rtt'", ()
        ),
        time_out=RawSQL(
            "test_keys->'advanced'->'timeouts'", ()
        ),
        package_loss=RawSQL(
            "test_keys->'advanced'->'packet_loss'", ()
        ),
    )

    def get_rows(self, rows):
        page_rows = super(NdtAjaxView, self).get_rows(rows)
        for row in page_rows:
            try:
                probe = Probe.objects.get(
                    identification=row['annotations']['probe'])
                probe_isp = probe.isp
                probe_plan = probe.plan
            except Probe.DoesNotExist:
                probe_isp = 'Unknown'
                probe_plan = 'Unknown'

            row['probe isp'] = probe_isp
            row['probe plan'] = probe_plan
            row['annotations'] = str(row['annotations'])

            try:
                row['% package loss'] = float(row['% package loss']) * 100
            except TypeError:
                row['% package loss'] = 'Unknown'

        return page_rows

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
