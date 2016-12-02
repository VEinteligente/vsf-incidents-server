from django.conf.urls import include, url
import views


urlpatterns = [
    url(
        r'^blocked_domains/$',
        views.BlockedDomains.as_view(),
        name='blocked_domains'
    ),
    url(
        r'^blocked_sites/$',
        views.BlockedSites.as_view(),
        name='blocked_sites'
    ),
    url(
        r'^list/$',
        views.EventList.as_view(),
        name='list'
    ),

]
