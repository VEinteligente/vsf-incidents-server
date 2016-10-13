# -*- coding: utf-8 -*-

from django.views import generic
from django.shortcuts import redirect


class IndexView(generic.View):

    def get(self, request):
        return redirect('patients:list')
