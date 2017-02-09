from django.shortcuts import render
from vsf.settings import FLAG_TESTS

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin

# from django.utils.module_loading import import_string
# app_label = "demo"
# url = import_string("plugins.%s" % FLAG_TESTS[0])


class PluginTableView(
    LoginRequiredMixin, PageTitleMixin, generic.TemplateView
):
    template_name = 'table.html'


class test(generic.TemplateView):
    template_name = 'table.html'

    def get(self, request, *args, **kwargs):
        # methodToCall = getattr(url, 'hola_hola')
        # result = methodToCall()
        # print url
        return super(test, self).get(request, args, kwargs)
