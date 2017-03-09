from django.shortcuts import render

from eztables.views import DatatablesView as EditableDatatablesView
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin

from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json

# from django.utils.module_loading import import_string
# app_label = "demo"
# url = import_string("plugins.%s" % FLAG_TESTS[0])


class PluginTableView(
    LoginRequiredMixin,
    PageTitleMixin,
    generic.TemplateView
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
