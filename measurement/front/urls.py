from django.conf.urls import url
from measurement.front import views

urlpatterns = [
    url(
        r'^$', views.LoginPrueba.as_view(), name='index'
    ),
    url(
        r'^measurement-table/$',
        views.MeasurementTableView.as_view(),
        name='measurement-table'
    ),
]
