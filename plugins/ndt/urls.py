from django.conf.urls import include, url
from .rest.views import ListNDT, ListDailyTest
import views

urlpatterns = [
    url(
        r'^table/$',
        views.NdtTableView.as_view(),
        name='ndt-table'
    ),
    url(
        r'^ndt-ajax/$',
        views.NdtAjaxView.as_view(),
        name='ndt-ajax'
    ),
    url(
        r'^speed-test-table/$',
        views.DailyTestTable.as_view(),
        name='speed-test-table'
    ),
    url(
        r'^speed-test-ajax/$',
        views.SpeedTestAjax.as_view(),
        name='measurements-ndt'
    ),
    url(
        r'^api/measurements-ndt/$',
        ListNDT.as_view(),
        name='speed-test-ajax'
    ),
    url(
        r'^api/daily-test/$',
        ListDailyTest.as_view(),
        name='measurements-ndt'
    ),
]
