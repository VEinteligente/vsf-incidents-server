from django.contrib import admin
from models import (
    DNSServer, Flag, Probe, State, Country, Plan, ISP, Metric,
)


class MetricAdmin(admin.ModelAdmin):
    list_filter = ('test_name', 'probe__identification')
    search_fields = ('measurement', 'input')


class FlagAdmin(admin.ModelAdmin):
    raw_id_fields = ('metric', 'target', 'event', 'suggested_events')
    list_filter = ('flag', 'manual_flag')
    search_fields = ('metric__measurement', 'metric__input')


admin.site.register(DNSServer)
admin.site.register(Flag, FlagAdmin)
admin.site.register(Probe)
admin.site.register(State)
admin.site.register(Country)
admin.site.register(Plan)
admin.site.register(ISP)
admin.site.register(Metric, MetricAdmin)
