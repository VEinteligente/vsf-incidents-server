from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from eztables.views import DatatablesView
from measurement.models import Flag
from .forms import EventForm
from event.models import Event
from django.utils.six import text_type
import json
import re

RE_FORMATTED = re.compile(r'\{(\w+)\}')


class CreateEvent(generic.CreateView):
    form_class = EventForm
    success_url = 'http://google.com'
    template_name = 'create_event.html'

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """

        flags = form.cleaned_data['flags'].split(' ')
        flags = Flag.objects.filter(medicion__in=flags)

        self.object = form.save(commit=False)

        if not form.cleaned_data['open_ended']:
            self.object.end_date = flags.latest('date').date

        self.object.start_date = flags.earliest('date').date
        self.object.isp = flags[0].isp
        self.object.target = flags[0].target

        self.object.save()

        flags.update(event=self.object)

        return HttpResponseRedirect(self.get_success_url())


class FlagsTable(DatatablesView):

    model = Flag
    queryset = Flag.objects.filter(event=None)
    fields = {
        'Flag': 'flag',
        'Measurement': 'medicion',
        'Date': 'date',
        'Target': 'target',
        'ISP': 'isp',
        'IP Address': 'ip',
        'Measurement type': 'type_med'
    }

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )
