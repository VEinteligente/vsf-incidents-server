from django.contrib import admin
from http.models import HTTP
from dns.models import DNS
from tcp.models import TCP
from ndt.models import NDT, DailyTest

admin.site.register(HTTP)
admin.site.register(DNS)
admin.site.register(TCP)
admin.site.register(NDT)
admin.site.register(DailyTest)
