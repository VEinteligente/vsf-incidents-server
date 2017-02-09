from django.shortcuts import render

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin


class PluginTableView(
    LoginRequiredMixin, PageTitleMixin, generic.TemplateView
):
    template_name = 'table.html'
