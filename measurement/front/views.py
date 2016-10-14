from django.shortcuts import render
from django.views import generic
from django.db import connections
import psycopg2


# Create your views here.


class MeasurementTableView(generic.TemplateView):

    template_name = 'dashboard/display_table.html'

    def get_context_data(self, **kwargs):

        context = super(MeasurementTableView,self).get_context_data(**kwargs)

        try:
            cursor = connections['titan_db'].cursor()
            cursor.execute("select * from metrics")
            # columns = [col[0] for col in cursor.description]
            # rows = [dict(zip(columns, row)) for row in cursor.fetchone()]
            rows = cursor.fetchone()
        finally:
            connections['titan_db'].close()

        context['rows'] = rows

        # print rows

        return context


class LoginPrueba(generic.TemplateView):

    template_name = 'measurement/list.html'
