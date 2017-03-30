from django.contrib import admin
from ndt.models import NDTMeasurement, DailyTest

admin.site.register(NDTMeasurement)
admin.site.register(DailyTest)
