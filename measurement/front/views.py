from django.shortcuts import render
from django.views.generic import TemplateView


class LoginPrueba(TemplateView):

    template_name = 'list.html'
