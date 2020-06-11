from django.contrib import admin
from .models import DNS, Flag, Probe, State, Country, Plan

admin.site.register(DNS)
admin.site.register(Flag)
admin.site.register(Probe)
admin.site.register(State)
admin.site.register(Country)
admin.site.register(Plan)
