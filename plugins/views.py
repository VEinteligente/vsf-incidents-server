from django.shortcuts import render

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin

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
            column = {}
            column['mData'] = title
            renders.append(column)
        return json.dumps(renders)

    def get_context_data(self, **kwargs):
        context = super(PluginTableView, self).get_context_data(**kwargs)
        context['titles'] = self.titles
        json = self.get_render_json()
        print (json)
        context['aoColumns_json'] = json
        if self.url_ajax is not None:
            context['url_ajax'] = self.url_ajax
        return context
