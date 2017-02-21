from django.views import generic
from eztables.views import DatatablesView
from measurement.models import Metric
from models import DayTest


class PuraPrueba(generic.TemplateView):

    template_name = 'table.html'

    def get(self, request, *args, **kwargs):
        print('1')
        metric = Metric.objects.all().first()
        dt = DayTest(metric=metric)
        dt.save()
        print('2')
        return super(PuraPrueba, self).get(args, kwargs)
