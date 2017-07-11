from django.contrib import admin
from http.models import HTTP
from dns.models import DNS
from tcp.models import TCP
from ndt.models import NDT, DailyTest


class PluginAdmin(admin.ModelAdmin):
    raw_id_fields = ("metric", "flag", "target")


class NDTAdmin(admin.ModelAdmin):
    raw_id_fields = ("metric", "flag", "isp", "daily_test")


admin.site.register(HTTP, PluginAdmin)
admin.site.register(DNS, PluginAdmin)
admin.site.register(TCP, PluginAdmin)
admin.site.register(NDT, NDTAdmin)
admin.site.register(DailyTest)
