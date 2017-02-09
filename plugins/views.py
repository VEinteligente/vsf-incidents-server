from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin
# Create your views here.


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
