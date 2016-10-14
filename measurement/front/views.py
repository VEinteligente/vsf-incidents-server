from django.shortcuts import render
from django.views import generic
from django.db import connections


# Create your views here.


class MeasurementTableView(generic.TemplateView):

    template_name = 'dashboard/display_table.html'

    def get_context_data(self, **kwargs):

        context = super(MeasurementTableView,self).get_context_data(**kwargs)

        # try:
        #     cursor = connections['titan_db'].cursor()
        #     cursor.execute("select * from metrics")
        #     rows = cursor.fetchone()
        # finally:
        #     connections['titan_db'].close()

        # context['rows'] = rows

        # print rows

        return context
