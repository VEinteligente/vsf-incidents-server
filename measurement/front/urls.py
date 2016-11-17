from django.conf.urls import url
from measurement.front import views

urlpatterns = [
    url(
        r'^$',
        views.MeasurementTableView.as_view(),
        name='measurement-table'
    ),
    url(
        r'^measurement-ajax/$',
        views.MeasurementAjaxView.as_view(),
        name='measurement-ajax'
    ),
    url(
        r'^dns-table/$',
        views.DNSTableView.as_view(),
        name='dns-table'
    ),
    url(
        r'^tcp-table/$',
        views.TCPTableView.as_view(),
        name='tcp-table'
    ),
    url(
        r'^http-table/$',
        views.HTTPTableView.as_view(),
        name='http-table'
    ),
    url(
        r'^http-table-ajax/$',
        views.HTTPListDatatablesView.as_view(),
        name='http-table-ajax'
    ),
    url(
        r'^prueba/$',
        views.PruebaDataTable.as_view(),
        name='test'
    ),
    url(
        r'^prueba-ajax/$',
        views.PruebaDataTableAjax.as_view()
    ),
]
