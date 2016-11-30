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
        r'^(?P<pk>[0-9]+)/change-status/$',
        views.ChangeEventStatus.as_view(),
        name='change-event-status'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete/$',
        views.DeleteEvent.as_view(),
        name='delete-event'
    ),
    url(
        r'^update-ajax/$',
        views.UpdateFlagsTable.as_view(),
        name='update-ajax'
    ),
    url(
        r'^$',
        views.ListEvent.as_view(),
        name='list-event'
    ),
    url(
        r'^suggestions/$',
        views.ListEventSuggestedFlags.as_view(),
        name='suggestions-event'
    ),
]
