from django.views import generic
from datetime import datetime
from eztables.views import DatatablesView
from measurement.models import Metric, Probe
from models import DayTest
# from measurement.models import Country, State, Probe
# import random


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
