# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageTitleMixin
from django.views import generic

from measurement.models import Metric, Flag, Probe
from event.models import Event
from Case.models import Case

class HomeView(LoginRequiredMixin, PageTitleMixin, generic.TemplateView):
    """HomeView: TemplateView than
    display the home page"""
    template_name = "dashboard/home.html"
    page_header = "VSF"
    page_header_description = "Home Page"
    breadcrumb = [""]

    def get_context_data(self, **kwargs):
        """ Insert in context all numbers and the last 10 rows of Cases,
        Events, Flags and Measurements"""
        context = super(HomeView, self).get_context_data(**kwargs)

        """ Events variables to insert in context"""
        events_num = Event.objects.count()
        events_sketch_num = Event.objects.filter(draft=True).count()
        events_publish_num = events_num - events_sketch_num
        events = Event.objects.all().order_by('-id')[:10]

        """ Cases variables to insert in context"""
        cases_num = Case.objects.count()
        cases_sketch_num = Case.objects.filter(draft=True).count()
        cases_publish_num = cases_num - cases_sketch_num
        cases = Case.objects.all().order_by('-id')[:10]

        """ Flags variables to insert in context"""
        flags = Flag.objects.all().order_by('-id')[:10]
        flags_num = Flag.objects.count()
        flags_hard_num = Flag.objects.filter(flag=Flag.HARD).count()
        flags_muted_num = Flag.objects.filter(flag=Flag.MUTED).count()
        flags_soft_num = Flag.objects.filter(flag=Flag.SOFT).count()

        """ Measurements variables to insert in context,
        including number of probes ans reports"""
        metrics_num = Metric.objects.count()
        metrics = Metric.objects.all().order_by('-id')[:10]
        context['probes_num'] = Probe.objects.count()
        context['reports_num'] = Metric.objects.values(
        	'report_id').distinct().count()

        context['metrics_num'] = metrics_num
        context['metrics'] = metrics
        context['flags'] = flags
        context['flags_num'] = flags_num
        context['flags_hard_num'] = flags_hard_num
        context['flags_soft_num'] = flags_soft_num
        context['flags_muted_num'] = flags_muted_num
        context['events_num'] = events_num
        context['events_sketch_num'] = events_sketch_num
        context['events_publish_num'] = events_publish_num
        context['events'] = events
        context['cases_num'] = cases_num
        context['cases_sketch_num'] = cases_sketch_num
        context['cases_publish_num'] = cases_publish_num
        context['cases'] = cases
        return context
