from django.conf.urls import url
from measurement.rest import views

urlpatterns = [
    url(
        r'^measurement_rest/$',
        views.MeasurementRestView.as_view(),
        name='measurement_rest'
    ),
    # url(
    #     r'^dns_rest/$',
    #     views.DNSMeasurementRestView.as_view(),
    #     name='dns_rest'
    # ),
    url(
        r'^flags/$',
        views.FlagListView.as_view(),
        name='flag_list'
    ),
    url(
        r'^soft-flags/$',
        views.SoftFlagListView.as_view(),
        name='soft_flag_list'
    ),
    url(
        r'^hard-flags/$',
        views.HardFlagListView.as_view(),
        name='hard_flag_list'
    ),
    url(
        r'^muted-flags/$',
        views.MutedFlagListView.as_view(),
        name='muted_flag_list'
    ),
    url(
        r'^flag/detail/(?P<flag_id>[^\/]+)/$',
        views.DetailFlagRestView.as_view(),
        name='detail-case-rest'
    ),
]
