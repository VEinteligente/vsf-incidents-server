# -*- encoding: utf-8 -*-
import json
import re

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic
from eztables.views import DatatablesView

from dashboard.mixins import PageTitleMixin
from event.models import Event, Target, Site
from event.utils import suggestedFlags
from measurement.models import Flag
from .forms import EventForm, EventExtendForm, EventEvidenceForm, SelectSiteForm

RE_FORMATTED = re.compile(r'\{(\w+)\}')


class ListEvent(LoginRequiredMixin, PageTitleMixin, generic.ListView):
    """ListEvent: ListView than
    display a list of all events"""
    model = Event
    template_name = "list_event.html"
    context_object_name = "events"
    page_header = "Events"
    page_header_description = "List of events"
    breadcrumb = ["Events"]


# Deprecated - each pluggin have his own create event
class CreateEvent(LoginRequiredMixin, PageTitleMixin, generic.CreateView):
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
            split = f.split('&')
            target = Target.objects.get(url=split[1])
            flag = Flag.objects.filter(
                Q(medicion=split[0],
                  target=target,
                  isp=split[2],
                  ip=split[3],
                  type_med=split[4]) |
                Q(medicion=split[0],
                  target=target,
                  isp=None,
                  ip=None,
                  type_med=split[4])
            )
            ids += [flag.first().id]

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
        if flags[0].isp is not None:
            self.object.isp = flags[0].isp  # Flag isp
        else:
            self.object.isp = "Unknown"
        self.object.target = flags[0].target  # Flag target

        self.object.save()  # Save object in the Database

        #self.object.flags.clear()  # Delete flags asociated

        self.object.flags = flags  # Add flags to object

        self.object.save()  # Save object with flags

        flags.update(event=self.object)

        # remove all events from the related flag
        for flag in flags:
            flag.suggested_events.clear()
        suggestedFlags(self.object)

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


# Deprecated - each pluggin have his own update event
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
        flags_id = ''

        for f in flags:
            flags_id += f.medicion + ' '
            try:
                flags_str += f.medicion + '&' + f.target.url + '&' + f.isp + '&' + f.ip + '&' + f.type_med + ' '
            except Exception:
                flags_str += f.medicion + '&' + f.target.url + '&Unknown&Unknown&' + f.type_med + ' '
        open_ended = False

        if not event.end_date:
            open_ended = True

        # Initial data for the form
        context['form'] = form(initial={'identification': event.identification,
                                        'flags': flags_str,
                                        'open_ended': open_ended
                                        })
        context['flags_id'] = flags_id

        return context


class ChangeEventStatus(LoginRequiredMixin, generic.UpdateView):
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


class DeleteEvent(LoginRequiredMixin, generic.DeleteView):
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

        msg = 'Event deleted sucessfully'

        messages.success(request, msg)

        return HttpResponseRedirect(self.success_url)

    def get(self, request, *args, **kwargs):

        return self.delete(request, *args, **kwargs)


class DetailEvent(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    """
    DetailEvent: DetailView than
    give the details of a specific Event object
    """
    http_method_names = [u'get', u'post']

    model = Event
    context_object_name = "event"
    template_name = "detail_event.html"
    page_header = "Event Details"
    page_header_description = ""
    breadcrumb = ["Events", "Event Details"]
    object = None

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if 'clear-suggested-flags' in request.POST:
            self.clear_suggested_flags()

        if 'search-suggested-flag' in request.POST:
            suggestedFlags(self.object)

        if 'add-selected-flags' in request.POST:
            self.add_selected_flags(request)

        if 'add-all-flags' in request.POST:
            self.add_all_flags()

        return self.render_to_response(context)

    def add_selected_flags(self, request):
        flags = request.POST['flags'].split('&')
        event = self.object
        flags = filter(None, flags)
        flags = Flag.objects.filter(
            uuid__in=flags
        )

        for flag in flags:
            if flag.flag == Flag.NONE and flag.manual_flag is False:
                flag.flag = Flag.SOFT
                flag.manual_flag = True
            flag.event = event
            flag.suggested_events.clear()
            flag.save()

    def add_all_flags(self):
        flags = Flag.objects.filter(
            suggested_events=self.object
        )

        for flag in flags:
            if flag.flag == Flag.NONE and flag.manual_flag is False:
                flag.flag = Flag.SOFT
                flag.manual_flag = True
            flag.event = self.object
            flag.suggested_events.clear()
            flag.save()

    def clear_suggested_flags(self):
        self.object.suggested_flags.clear()
        self.object.save()


class SuggestedFlagsTable(DatatablesView):
    """FlagsTable: DatatablesView used to display
    a list of metrics with flags. This View is summoned by AJAX"""
    pk_url_kwarg = 'pk'
    model = Flag
    queryset = Flag.objects.filter(event=None)
    fields = {
        'Checkbox': 'uuid',
        'Measurement': 'metric__measurement',
        'Flag': 'flag',
        'Date': 'metric_date',
        'ISP': 'metric__probe__isp__name',
        'Probe': 'metric__probe__identification'
    }

    def get_queryset(self):
        """
        Apply Datatables sort and search criterion to QuerySet
        :return: queryset
        """
        event_pk = self.kwargs.get(self.pk_url_kwarg)
        event = Event.objects.get(id=event_pk)
        flags = event.suggested_flags.values('id')
        self.queryset = Flag.objects.filter(id__in=flags)
        return super(SuggestedFlagsTable, self).get_queryset()

    def json_response(self, data):
        """Json response"""
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )


# Deprecated - each pluggin have his own data table flag ajax
class FlagsTable(LoginRequiredMixin, DatatablesView):
    """FlagsTable: DatatablesView used to display
    a list of metrics with flags. This View is summoned by AJAX"""
    pk_url_kwarg = 'pk'
    model = Flag
    queryset = Flag.objects.filter(event=None)
    fields = {
        'Measurement': 'metric',
        'Flag': 'flag',
        'Date': 'metric_date',
        'ISP': 'metric_date',
        'Probe': 'metric__probe__identification'
    }

    def json_response(self, data):
        """Json response"""
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )


class UpdateFlagsTable(LoginRequiredMixin, DatatablesView):
    """UpdateFlagsTable: DatatablesView used to display
    a list of metrics with flags of an event to be updated.
    This View is summoned by AJAX"""
    model = Flag
    fields = {
        'id': 'id',
        'Flag': 'flag',
        'Measurement': 'medicion',
        'Date': 'date',
        'Target': 'target__url',
        'ISP': 'isp',
        'IP Address': 'ip',
        'Measurement type': 'type_med',
        'selected': 'selected'
    }

    def get_queryset(self):
        """Flag list"""

        pk = self.request.GET.get('pk')

        # Flags of the measurement
        if pk:
            queryset = Flag.objects.filter(
                Q(event=None) |
                Q(event=Event.objects.get(id=pk))
            ).annotate(selected=Count(
                Case(
                    When(event=Event.objects.get(id=pk), then=1),
                    output_field=IntegerField()))
            ).order_by('-selected')

        # Perform global search
        queryset = self.global_search(queryset)
        # Perform column search
        queryset = self.column_search(queryset)
        # Return the ordered queryset
        return queryset.order_by(*self.get_orders())

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )


class ListEventSuggestedFlags(LoginRequiredMixin, PageTitleMixin, generic.TemplateView):
    """ListEventSuggestedFlags: ListView than
    display a list of all events with suggested flags"""
    model = Event
    template_name = "list_eventflagmatch.html"
    context_object_name = "suggestions"
    page_header = "Event Suggestions"
    page_header_description = "Matches between existing events and hard flags"
    breadcrumb = ["Events", "Event Suggestions"]


class ListEventSuggestedFlagsAjax(LoginRequiredMixin, DatatablesView):
    queryset = Event.objects.exclude(
        suggested_flags=None
    ).prefetch_related(
        'suggested_flags',
        'flags'
    ).annotate(
        count_flags=Count('flags'),
        count_suggested_flags=Count('suggested_flags')
    )
    fields = {
        'id': 'id',
        'Event': 'identification',
        'Type': 'plugin_name',
        'Current Flags': 'count_flags',
        'Suggested Flags': 'count_suggested_flags',
        'ISP': 'isp__name',
        'Target': 'target__url',
        'Start': 'start_date',
        'Finish': 'end_date',
        'Status': 'draft'
    }

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )


class ListTargets(LoginRequiredMixin, PageTitleMixin, generic.FormView):
    form_class = SelectSiteForm
    template_name = "list_targets.html"
    page_header = "Targets List"
    page_header_description = "List of targets"
    breadcrumb = ["Events", "Targets"]
    success_url = reverse_lazy('events:event_front:targets-list')
    site = None
    target = None

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        try:
            self.target = Target.objects.get(
                id=form.cleaned_data['target']
            )
        except Site.DoesNotExist:
            raise Http404("target does not exist")

        self.target.site = form.cleaned_data['site']
        self.target.save()

        return HttpResponseRedirect(self.get_success_url())


class ListTargetsAjax(LoginRequiredMixin, DatatablesView):
    queryset = Target.objects.prefetch_related('site__name')
    fields = {
        'ID': 'id',
        'Type': 'type',
        'Site': 'site__name',
        'Domain': 'domain',
        'URL': 'url',
        'IP_Address': 'ip'
    }

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
        )


# Deprecated - each pluggin have his own create event
class CreateEventMeasurementView(
    UpdateEvent,
    PageTitleMixin,
    generic.UpdateView
):
    """CreateEventMeasurementView: CreateView extends of UpdateEvent than
    create a new event from a list of measurements"""
    form_class = EventExtendForm
    context_object_name = 'event'
    page_header = "New Event"
    page_header_description = ""
    breadcrumb = ["Events", "New Event from Measurements"]
    model = Event
    template_name = 'create_event_measurement.html'

    def get_context_data(self, **kwargs):
        '''Initial data for Event form'''

        context = super(CreateEventMeasurementView, self).get_context_data(**kwargs)

        form = self.get_form_class()

        event = self.object
        flags = event.flags.values_list('id', flat=True)
        flags = Flag.objects.filter(id__in=flags)

        open_ended = False

        if not event.end_date:
            open_ended = True

        # Initial data for the form
        context['form'] = form(initial={'identification': event.identification,
                                        'open_ended': open_ended,
                                        'isp': event.isp,
                                        'type': event.type,
                                        'flags_type': flags.first().type_med
                                        })
        context['flags'] = flags
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # Get flags values
        event = self.object
        flags = event.flags.values_list('id', flat=True)
        flags = Flag.objects.filter(id__in=flags)
        flags_type = form.cleaned_data['flags_type']

        # Object to save
        self.object = form.save(commit=False)

        if Event.objects.filter(id=self.object.id).exists():
            msg = 'Event modified successfully'
        else:
            msg = 'Event Created successfully'

        if not form.cleaned_data['open_ended']:
            self.object.end_date = flags.latest('date').date
        else:
            self.object.end_date = None

        self.object.save()  # Save object in the Database

        # remove all events from the related flag
        for flag in flags:
            flag.suggested_events.clear()
            flag.type_med = flags_type
            flag.save()
        suggestedFlags(self.object)

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


# Event with external evidence views
# Deprecated - each pluggin have his own create event
# (this include events with measurement)
class CreateEventEvidenceView(
    LoginRequiredMixin,
    PageTitleMixin,
    generic.CreateView
):
    """
    CreateEventEvidenceView: CreateView for create
    Event with external evidence
    """
    form_class = EventEvidenceForm
    page_header = "New Event with External Evidence"
    page_header_description = ""
    breadcrumb = ["Events", "New Event with External Evidence"]
    success_url = reverse_lazy('events:event_front:list-event')
    template_name = 'create_event_evidence.html'

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        if (form.cleaned_data['end_date'] is None) and (form.cleaned_data['open_ended'] is False):
            form.add_error(
                None,
                'You must give an end date to this event or select open ended'
            )
            form.add_error('end_date', '')
            form.add_error('open_ended', '')
            return self.form_invalid(form)
        # Object to save
        self.object = form.save(commit=False)

        if Event.objects.filter(id=self.object.id).exists():
            msg = 'Se ha modificado el evento'
        else:
            msg = 'Se ha creado el evento'

        if form.cleaned_data['open_ended']:
            self.object.end_date = None

        # Get or create Url object to be used as event target
        target, created = Target.objects.get_or_create(
            site=form.cleaned_data['target_site'],
            url=form.cleaned_data['target_url'],
            ip=form.cleaned_data['target_ip'])

        self.object.target = target

        self.object.save()  # Save object in the Database

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


# Deprecated - each pluggin have his own update event
# (this include events with measurement)
class UpdateEventEvidenceView(
    LoginRequiredMixin,
    PageTitleMixin,
    generic.UpdateView
):
    """
    UpdateEventEvidenceView: UpdateView for update 
    Event with external evidence
    """
    model = Event
    context_object_name = 'event'
    form_class = EventEvidenceForm
    page_header = "Update Event with External Evidence"
    page_header_description = ""
    breadcrumb = ["Events", "Update Event with External Evidence"]
    success_url = reverse_lazy('events:event_front:list-event')
    template_name = 'create_event_evidence.html'

    def get_form(self, form_class=None):
        form = super(UpdateEventEvidenceView, self).get_form(form_class)
        # get event to be updated
        event = Event.objects.get(id=self.kwargs['pk'])

        # get initial values of target attributes
        form.fields['target_ip'].initial = event.target.ip
        form.fields['target_url'].initial = event.target.url
        form.fields['target_site'].initial = event.target.site

        # check if event is open ended
        if event.end_date is None:
            form.fields['open_ended'].initial = True
        return form

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        if (form.cleaned_data['end_date'] is None) and (form.cleaned_data['open_ended'] is False):
            form.add_error(
                None,
                'You must give an end date to this event or select open ended'
            )
            form.add_error('end_date', '')
            form.add_error('open_ended', '')
            return self.form_invalid(form)
        # Object to save
        self.object = form.save(commit=False)

        if Event.objects.filter(id=self.object.id).exists():
            msg = 'Se ha modificado el evento'
        else:
            msg = 'Se ha creado el evento'

        if form.cleaned_data['open_ended']:
            self.object.end_date = None

        # Get or create Url object to be used as event target
        target, created = Target.objects.get_or_create(
            site=form.cleaned_data['target_site'],
            url=form.cleaned_data['target_url'],
            ip=form.cleaned_data['target_ip'])

        self.object.target = target

        self.object.save()  # Save object in the Database

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())
