from django.conf.urls import url
from Case.rest import views

urlpatterns = [
    url(
        r'^list/$',
        views.ListCaseView.as_view(),
        name='list-case-rest'
    ),
    url(
        r'^detail/(?P<case_id>[0-9]+)/$',
        views.DetailCaseRestView.as_view(),
        name='detail-case-rest'
    ),
    url(
        r'^detail_event/(?P<case_id>[0-9]+)/$',
        views.DetailEventCaseRestView.as_view(),
        name='detail-event-case-rest'
    ),
    url(
        r'^list/region/$',
        views.ListRegionCaseView.as_view(),
        name='list-region-case-rest'
    ),
]
