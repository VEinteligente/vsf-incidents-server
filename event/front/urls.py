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

]
