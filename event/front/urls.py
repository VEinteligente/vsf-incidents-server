from django.conf.urls import include, url
import views


urlpatterns = [
    url(
        r'^create/$',
        views.CreateEvent.as_view(),
        name='create-event'
    ),
    url(
        r'^create-ajax/$',
        views.FlagsTable.as_view(),
        name='create-ajax'
    ),
    url(
        r'^(?P<pk>[0-9]+)/update/$',
        views.UpdateEvent.as_view(),
        name='update-event'
    ),
    url(
        r'^$',
        views.ListEvent.as_view(),
        name='list-event'
    ),
]
