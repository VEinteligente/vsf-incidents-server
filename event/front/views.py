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
        # Get flags values
        flags = form.cleaned_data['flags'].split(' ')
        ids = []

        for f in flags:
            split = f.split('/')
            flag = Flag.objects.filter(medicion=split[0],
                                       target=split[1],
                                       isp=split[2],
                                       ip=split[3],
                                       type_med=split[4])
            ids += [flag[0].id]

        # Filter Flag objects for ids
        flags = Flag.objects.filter(id__in=ids)

        # Object to save
        self.object = form.save(commit=False)

        if Event.objects.filter(id=self.object.id).exists():
            msg = 'Se ha modificado el evento'
        else:
            msg = 'Se ha creado el evento'

        if not form.cleaned_data['open_ended']:
            self.object.end_date = flags.latest('date').date
        else:
            self.object.end_date = None

        self.object.start_date = flags.earliest('date').date
        self.object.isp = flags[0].isp  # Flag isp
        self.object.target = flags[0].target  # Flag target

        self.object.save()  # Save object in the Database

        self.object.flags = flags  # Add flags to object

        self.object.save()  # Save object with flags

        flags.update(event=self.object)

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


class UpdateEvent(CreateEvent,
                  PageTitleMixin,
                  generic.UpdateView):
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
        '''Initial data for Event form'''

        context = super(UpdateEvent, self).get_context_data(**kwargs)

        form = self.get_form_class()

        event = self.object
        flags = event.flags.values_list('id', flat=True)
        flags = Flag.objects.filter(id__in=flags)

        flags_str = ''

        for f in flags:
            flags_str += f.medicion + '/' + f.target + '/' + \
                         f.isp + '/' + f.ip + '/' + f.type_med + ' '

        open_ended = False

        if not event.end_date:
            open_ended = True

        # Initial data for the form
        context['form'] = form(initial={'identification': event.identification,
                                        'flags': flags_str,
                                        'open_ended': open_ended
                                        })

        return context


class ChangeEventStatus(generic.UpdateView):
    """ChangeEventStatus: Change Event status.
    It can be Public or Draft. Draft for default"""
    model = Event
    success_url = reverse_lazy('events:event_front:list-event')

    def get(self, request, *args, **kwargs):
        '''If event.draft is True change it to False.
        If event.draft is False change it to True'''

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
        """Delete Event and make its flags availables"""

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
        """Json response"""
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
        """Flag list"""

        pk = self.request.GET.get('pk')

        # Flags of the measurement
        if pk:
            queryset = Flag.objects.filter(Q(event=None) |
                                           Q(event=Event.objects.get(id=pk)))

        return queryset

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )


class ListEventSuggestedFlags(PageTitleMixin, generic.ListView):
    """ListEventSuggestedFlags: ListView than
    display a list of all events with suggested flags"""
    model = Event
    template_name = "list_eventflagmatch.html"
    context_object_name = "suggestions"
    page_header = "Event Suggestions"
    page_header_description = "Matches between existing events and hard flags"
    breadcrumb = ["Events", "Event Suggestions"]
    queryset = Event.objects.exclude(
        suggested_events=None).prefetch_related('suggested_events', 'flags')
