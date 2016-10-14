from django.conf.urls import url
import views

urlpatterns = [
    url(
        r'^measurement-table/$',
        views.MeasurementTableView.as_view(),
        name='measurement-table'
    ),
]
