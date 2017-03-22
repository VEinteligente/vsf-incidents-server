from django.conf.urls import url
import views

urlpatterns = [
    url(
        r'^table/$',
        views.HTTPTableView.as_view(),
        name='http-table'
    ),
    url(
        r'^http-ajax/$',
        views.HTTPAjaxView.as_view(),
        name='http-ajax'
    ),
]
