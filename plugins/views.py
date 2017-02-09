from django.shortcuts import render
from vsf.settings import FLAG_TESTS

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin

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

    def get_render_json(self):
        renders = []
        for title in self.titles:
            column = {"mData": title}
            renders.append(column)
        return renders

    def get_context_data(self, **kwargs):
        context = super(PluginTableView, self).get_context_data(**kwargs)
        context['titles'] = self.titles
        context['aoColumns_json'] = self.get_render_json()
        return context


class test(generic.TemplateView):
    template_name = 'table.html'

    def get(self, request, *args, **kwargs):
        # methodToCall = getattr(url, 'hola_hola')
        # result = methodToCall()
        # print url
        return super(test, self).get(request, args, kwargs)

