from django.shortcuts import render

from eztables.views import DatatablesView as EditableDatatablesView
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin

from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
import time

from event.front.forms import EventEvidenceForm
from event.models import Event

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
    form_class = EventEvidenceForm
    enable_event = False

    def get_render_json(self):
        renders = []
        for title in self.titles:
            column = {'mData': title}
            renders.append(column)
        return json.dumps(renders)

    def get_context_data(self, **kwargs):
        context = super(PluginTableView, self).get_context_data(**kwargs)
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
        context['titles'] = self.titles
        json = self.get_render_json()
        context['aoColumns_json'] = json
        if self.url_ajax is not None:
            context['url_ajax'] = self.url_ajax
        return context


class DatatablesView(EditableDatatablesView):

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )
