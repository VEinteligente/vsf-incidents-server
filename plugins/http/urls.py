from django.conf.urls import url
import views

urlpatterns = [
    url(
        r'^table/$',
        views.HTTPTableView.as_view(),
        name='http-table'
    ),
    url(
        r'^(?P<pk>[0-9]+)/update/$',
        views.HTTPUpdateEventView.as_view(),
        name='http-update-event'
    ),
    url(
        r'^http-ajax/$',
        views.HTTPAjaxView.as_view(),
        name='http-ajax'
    ),
]
