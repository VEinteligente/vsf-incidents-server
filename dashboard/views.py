# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin
from django.views import generic


class HomeView(LoginRequiredMixin, PageTitleMixin, generic.TemplateView):
    """ListCase: ListView than
    display a list of all cases"""
    template_name = "dashboard/home.html"
    page_header = "VSF"
    page_header_description = "Home Page"
    breadcrumb = [""]

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context
