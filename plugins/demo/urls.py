from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(
        r'^table/$',
        views.DemoTableView.as_view(),
        name='demo-table'
    ),
    url(
        r'^demo-ajax/$',
        views.DemoAjaxView.as_view(),
        name='demo-ajax'
    ),
]
