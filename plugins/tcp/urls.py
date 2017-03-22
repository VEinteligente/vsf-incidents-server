from django.conf.urls import url
import views

urlpatterns = [
    url(
        r'^table/$',
        views.TCPTableView.as_view(),
        name='tcp-table'
    ),
    url(
        r'^tcp-ajax/$',
        views.TCPAjaxView.as_view(),
        name='tcp-ajax'
    ),
]
