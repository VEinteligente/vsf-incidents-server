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
        r'^create/$',
        views.CreateMutedInput.as_view(),
        name='create-muted-input'
    ),
    url(
        r'^list-muted-input/$',
        views.ListMutedInput.as_view(),
        name='list-muted-input'
    ),
    url(
        r'^(?P<id>[\w-]+)/detail/$',
        views.MeasurementDetail.as_view(),
        name='detail-measurement'
    ),
    url(
        r'^(?P<pk>[0-9]+)/detail-muted-input/$',
        views.DetailMutedInput.as_view(),
        name='detail-muted-input'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete-muted-input/$',
        views.DeleteMutedInput.as_view(),
        name='delete-muted-input'
    ),
    url(
        r'^(?P<pk>[0-9]+)/edit-muted-input/$',
        views.UpdateMutedInput.as_view(),
        name='edit-muted-input'
    ),
    url(
        r'^create-probe/$',
        views.CreateProbe.as_view(),
        name='create-probe'
    ),
    url(
        r'^list-probe/$',
        views.ListProbe.as_view(),
        name='list-probe'
    ),
    url(
        r'^(?P<pk>[0-9]+)/detail-probe/$',
        views.DetailProbe.as_view(),
        name='detail-probe'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete-probe/$',
        views.DeleteProbe.as_view(),
        name='delete-probe'
    ),
    url(
        r'^(?P<pk>[0-9]+)/edit-probe/$',
        views.UpdateProbe.as_view(),
        name='edit-probe'
    ),
    url(
        r'^create-manual-flags/$',
        views.ManualFlagsView.as_view(),
        name='create-manual-flags'
    ),
    url(
        r'^reports/$',
        views.ListReportView.as_view(),
        name='list-report'
    ),
    url(
        r'^reports/(?P<report_id>\w+)/$',
        views.DetailReportView.as_view(),
        name='detail-report'
    ),
    url(
        r'^reports/probe/(?P<pk>\w+)$',
        views.ListReportProbeView.as_view(),
        name='list-report-probe'
    ),
    url(
        r'^create_event/$',
        views.EventFromMeasurementView.as_view(),
        name='measurements_to_event'
    ),
    url(
        r'^create_event/DNS/$',
        views.EventFromDNSMeasurementView.as_view(),
        name='measurements_to_event'
    ),
    url(
        r'^create_event/TCP/$',
        views.EventFromTCPMeasurementView.as_view(),
        name='measurements_to_event'
    ),
    url(
        r'^create_event/HTTP/$',
        views.EventFromHTTPMeasurementView.as_view(),
        name='measurements_to_event'
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
    url(
        r'^prueba-dns/$',
        views.DNSTableAjax.as_view()
    ),
    url(
        r'^datatable-tcp/$',
        views.TCPTableAjax.as_view()
    ),
]
