from django.conf.urls import url
import views

urlpatterns = [
    url(
        r'^table/$',
        views.DNSTableView.as_view(),
        name='dns-table'
    ),
    url(
        r'^dns-ajax/$',
        views.DNSAjaxView.as_view(),
        name='dns-ajax'
    ),
]
