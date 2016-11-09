from django.shortcuts import render
from django.views import generic
from .forms import EventForm


class CreateEvent(generic.CreateView):
    form_class = EventForm
    template_name = 'create_event.html'
