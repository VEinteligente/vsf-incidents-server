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
    url(
        r'^list-event-group/$',
        views.ListEventGroupView.as_view(),
        name='list-event-group'
    ),
    url(
        r'^sites/$',
        views.ListSiteView.as_view(),
        name='sites-rest'
    ),
    url(
        r'^sites/detail/(?P<site_name>[\w\-]+)/$',
        views.DetailSiteView.as_view(),
        name='detail-site-rest'
    ),
    url(
        r'^isp/$',
        views.ListISPView.as_view(),
        name='isp-rest'
    ),
    url(
        r'^categories/$',
        views.ListCategoriesView.as_view(),
        name='categories-rest'
    ),
    url(
        r'^targets/$',
        views.ListTargetsView.as_view(),
        name='targets-rest'
    ),

]
