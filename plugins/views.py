from django.shortcuts import render

from datetime import datetime, date
from eztables.views import DatatablesView as EditableDatatablesView
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin

from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
import time
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect

from event.front.forms import EventEvidenceForm
from event.models import Event, Target, ISP, Site
from event.utils import suggestedFlags
from measurement.models import Flag

from .forms import DataTableRangePicker

# from django.utils.module_loading import import_string
# app_label = "demo"
# url = import_string("plugins.%s" % FLAG_TESTS[0])


class PluginTableView(
    LoginRequiredMixin,
    PageTitleMixin,
    generic.FormView
):
    template_name = 'table.html'
    page_header = "Measurement List"
    page_header_description = ""
    breadcrumb = [""]
    titles = ["", ]
    url_ajax = None

    def get_render_json(self):
        renders = []
        for title in self.titles:
            column = {'mData': title}
            renders.append(column)
        return json.dumps(renders)

    def get_context_data(self, **kwargs):
        context = super(PluginTableView, self).get_context_data(**kwargs)
        context['titles'] = self.titles
        aux_json = self.get_render_json()
        context['aoColumns_json'] = aux_json
        if self.url_ajax is not None:
            context['url_ajax'] = self.url_ajax

        date_from = self.request.GET.get('date_from', date.today())
        date_to = self.request.GET.get('date_to', date.today())

        context['datepicker_form'] = DataTableRangePicker(
            initial={
                'date_from': date_from,
                'date_to': date_to
            }
        )
        return context


class PluginCreateEventView(
    PluginTableView,
    generic.CreateView
):
    model = Event
    success_url = reverse_lazy('events:event_front:list-event')
    form_class = EventEvidenceForm
    enable_event = False

    def get_context_data(self, **kwargs):
        context = super(PluginCreateEventView, self).get_context_data(**kwargs)
        if self.enable_event is False:
            context['form'] = None
        else:
            form = context['form']
            # create identification for the event (must be unique)
            num_events = Event.objects.count()
            identification = "event_" + str(num_events)
            identification += "_" + time.strftime("%x") + "_" + time.strftime("%X")
            form.fields['identification'].initial = identification
            context['form'] = form
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # Get flags values

        # Object to save
        self.object = form.save(commit=False)

        # Case Event with flags
        if form.cleaned_data['flags'] != "":
            ###################################################
            # Get Flags
            ###################################################
            flags = form.cleaned_data['flags'].split('&')

            flags = filter(None, flags)
            flags = Flag.objects.filter(
                uuid__in=flags
            ).select_related(
                'metric__probe__isp'
            )

            ###################################################
            # Get input and isp from flags.
            # I have the warranty
            # than these are the same for all
            # this flags thanks to form validation
            ###################################################
            flags_input = flags.first().metric.input
            try:
                flags_isp = flags.first().dnss.resolver_hostname
                flags_isp = ISP.objects.get(name=flags_isp)
            except Exception:
                try:
                    flags_isp = flags.first().metric.probe.isp
                except Exception:
                    flags_isp = None

            self.object.isp = flags_isp

            try:
                region = flags.first().metric.probe.region
            except Exception:
                region = None

            self.object.region = region
            self.object.target = flags.first().target

            ###################################################
            # Get Start and End date (Considering open ended case)
            ###################################################
            if not form.cleaned_data['open_ended']:
                if form.cleaned_data['end_date'] is None:
                    self.object.end_date = flags.latest(
                        'metric_date').metric_date
            else:
                self.object.end_date = None

            if form.cleaned_data['start_date'] is None:
                self.object.start_date = flags.earliest(
                    'metric_date').metric_date
            ###################################################
            # Get type of flags
            ###################################################

            flag = flags.first()
            self.object.plugin_name = flag.plugin_name

            ###################################################
            # Save Event in database
            ###################################################

            self.object.save()

            ###################################################
            # Set Any no flag into soft manual flag
            # Associate every flag to new event
            # Clear every suggested event on each flag
            ###################################################
            for flag in flags:
                if flag.flag == Flag.NONE and flag.manual_flag is False:
                    flag.flag = Flag.SOFT
                    flag.manual_flag = True
                flag.event = self.object
                flag.suggested_events.clear()
                flag.save()

            ###################################################
            # Associated suggested hard flags to new event
            ###################################################

            suggestedFlags(self.object)

        # Case Event with no flags
        else:
            ###################################################
            # Get Target from form fields
            ###################################################
            target, created = Target.objects.get_or_create(
                site=form.cleaned_data['target_site'],
                url=form.cleaned_data['target_url'],
                ip=form.cleaned_data['target_ip']
            )

            self.object.target = target
            ###################################################
            # Set End date none in open ended case
            ###################################################
            if form.cleaned_data['open_ended']:
                self.object.end_date = None

            ###################################################
            # Save Event in database
            ###################################################

            self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class PluginUpdateEventView(
    PluginCreateEventView,
    generic.UpdateView
):
    model = Event
    success_url = reverse_lazy('events:event_front:list-event')

    def get_context_data(self, **kwargs):
        """
        Initial data for Event form
        """

        context = super(PluginUpdateEventView, self).get_context_data(**kwargs)

        form = self.get_form_class()

        event = self.object

        ########################################################
        # Get all FLAG's UUID associated to this event
        # and create and string with format 'uuid&uuid&...'
        # to be initialized in flags field
        ########################################################

        flags = event.flags.values_list('id', flat=True)
        flags = Flag.objects.filter(id__in=flags).values_list('uuid')

        flags_str = ''

        for uuid in flags:
            flags_str += str(uuid[0]) + '&'

        ########################################################
        # Determinate if event is open-ended
        ########################################################

        open_ended = False

        if not event.end_date:
            open_ended = True

        ########################################################
        # Get target fields
        ########################################################

        target_ip = event.target.ip
        target_url = event.target.url
        target_site = event.target.site

        ########################################################
        # Initial data for the form
        ########################################################
        if self.request.method in ('GET'):
            context['form'] = form(
                instance=event,
                initial={
                    'flags': flags_str,
                    'open_ended': open_ended,
                    'target_site': target_site,
                    'target_url': target_url,
                    'target_ip': target_ip
                }
            )
        return context


class SuggestedEventsAjax(LoginRequiredMixin, generic.View):
    http_method_names = [u'get', ]
    flag = None

    def get(self, request, *args, **kwargs):
        try:

            self.flag = Flag.objects.get(uuid=request.GET['flag'])
        except Flag.DoesNotExist:
            return JsonResponse(
                {
                    'status': 'false',
                    'message': 'No matching flag'
                },
                status=404
            )

        events = self.flag.suggested_events.all()

        response = []

        for event in events:
            start_date = datetime.date(event.start_date).strftime('%b. %d, %Y, %I:%M %p')
            if event.end_date is None:
                end_date = 'Open ended'
            else:
                end_date = datetime.date(event.end_date).strftime('%b. %d, %Y, %I:%M %p')

            node = {
                'id': event.id,
                'name': event.identification,
                'isp': event.isp.name,
                'start': start_date,
                'end': end_date
            }
            response.append(node)

        return JsonResponse({'events': response})


class DatatablesView(EditableDatatablesView):

    def get_queryset(self):
        """
        Model in queryset must have a field named metric. This field must be
        a reference to Metric Model.
        """
        queryset = super(DatatablesView, self).get_queryset()

        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)
        if date_from:
            queryset = queryset.filter(
                metric__measurement_start_time__gte=date_from
            )
        if date_to:
            queryset = queryset.filter(
                metric__measurement_start_time__lte=date_to
            )
        return queryset

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )
