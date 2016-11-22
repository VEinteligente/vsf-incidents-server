# -*- encoding: utf-8 -*-
from django.views import generic
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from eztables.views import DatatablesView
from measurement.models import Flag
from django.db.models import Q
from .forms import EventForm
from event.models import Event
import json
import re

from dashboard.mixins import PageTitleMixin
from django.core.urlresolvers import reverse_lazy

RE_FORMATTED = re.compile(r'\{(\w+)\}')


class ListEvent(PageTitleMixin, generic.ListView):
    """ListEvent: ListView than
    display a list of all events"""
    model = Event
    template_name = "list_event.html"
    context_object_name = "events"
    page_header = "Events"
    page_header_description = "List of events"
    breadcrumb = ["Events"]


class CreateEvent(PageTitleMixin, generic.CreateView):
    """CreateEvent: CreateView than
    create a new Event object in DB"""
    form_class = EventForm
    page_header = "New Event"
    page_header_description = ""
    breadcrumb = ["Events", "New Event"]
    success_url = reverse_lazy('events:event_front:list-event')
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

        self.object.flags = flags

        self.object.save()

        flags.update(event=self.object)

        msg = 'Se ha creado el evento'

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


class UpdateEvent(PageTitleMixin, generic.UpdateView):
    """UpdateEvent: UpdateView than
    update an Event object in DB"""
    form_class = EventForm
    context_object_name = 'event'
    page_header = "Update Event"
    page_header_description = ""
    breadcrumb = ["Events", "Edit Event"]
    model = Event
    success_url = reverse_lazy('events:event_front:list-event')
    template_name = 'update_event.html'

    def get_context_data(self, **kwargs):

        context = super(UpdateEvent,self).get_context_data(**kwargs)

        form = self.get_form_class()

        event = self.object
        flags = event.flags.values_list('medicion', flat=True)
        flags_str = " ".join(flags)

        open_ended = False

        if not event.end_date:
            open_ended = True

        # Initial data for the form
        context['form'] = form(initial={'identification': event.identification,
                                        'flags': flags_str,
                                        'open_ended': open_ended
                                        })

        return context

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """

        flags = form.cleaned_data['flags'].split(' ')
        flags = Flag.objects.filter(medicion__in=flags)

        self.object = form.save(commit=False)

        if not form.cleaned_data['open_ended']:
            self.object.end_date = flags.latest('date').date
        else:
            self.object.end_date = None

        self.object.start_date = flags.earliest('date').date
        self.object.isp = flags[0].isp
        self.object.target = flags[0].target
        self.object.save()

        self.object.flags = flags

        self.object.save()

        flags.update(event=self.object)

        return HttpResponseRedirect(self.get_success_url())


class ChangeEventStatus(generic.UpdateView):
    """ChangeEventStatus: Change Event status.
    It can be Public or Draft. Draft for default"""
    model = Event
    success_url = reverse_lazy('events:event_front:list-event')

    def get(self, request, *args, **kwargs):
        event = self.model.objects.get(id=kwargs['pk'])

        if event.draft:
            event.draft = False
            msg = u'Se ha actualizado el estado del evento a Público'
        else:
            event.draft = True
            msg = u'Se ha actualizado el estado del evento a Borrador'

        event.save(update_fields=['draft'])

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.success_url)

class DeleteEvent(generic.DeleteView):
    """DeleteEvent: Delete event and make its measurements
    availables for others events"""
    model = Event
    template_name = 'list_event.html'
    success_url = reverse_lazy('events:event_front:list-event')

    def delete(self, request, *args, **kwargs):

        event = self.get_object()
        flags = event.flags.all()

        for f in flags:
            f.event = None
            f.save(update_fields=['event'])

        event.flags.remove()

        event.delete()

        msg = 'Se ha eliminado el evento elegido'

        messages.success(request, msg)

        return HttpResponseRedirect(self.success_url)

    def get(self, request, *args, **kwargs):

        return self.delete(request, *args, **kwargs)


class FlagsTable(DatatablesView):
    """FlagsTable: DatatablesView used to display
    a list of metrics with flags. This View is summoned by AJAX"""
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


class UpdateFlagsTable(DatatablesView):
    """UpdateFlagsTable: DatatablesView used to display
    a list of metrics with flags of an event to be updated.
    This View is summoned by AJAX"""
    model = Flag
    fields = {
        'Flag': 'flag',
        'Measurement': 'medicion',
        'Date': 'date',
        'Target': 'target',
        'ISP': 'isp',
        'IP Address': 'ip',
        'Measurement type': 'type_med'
    }

    def get_queryset(self):

        pk = self.request.GET.get('pk')

        if pk:
            queryset = Flag.objects.filter(Q(event=None) |
                                           Q(event=Event.objects.get(id=pk)))

        return queryset

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )
