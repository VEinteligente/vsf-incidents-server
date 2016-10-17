from django.conf.urls import url
from measurement.front import views

urlpatterns = [
    url(
        r'^$',
        views.MeasurementTableView.as_view(),
        name='measurement-table'
    ),
]
