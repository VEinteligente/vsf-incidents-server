from django.conf.urls import url
from measurement.rest import views

urlpatterns = [
    url(
        r'^measurement_rest/$',
        views.MeasurementRestView.as_view(),
        name='measurement_rest'
    ),
    url(
        r'^dns_rest/$',
        views.DNSMeasurementRestView.as_view(),
        name='dns_rest'
    )
]
