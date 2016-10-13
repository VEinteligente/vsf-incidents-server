from django.conf.urls import url, include

from dashboard import views

urlpatterns = [
    url(
        r'^$', views.IndexView.as_view(), name='index'
    ),
    url(
        r'^users/',
        include('users.urls', namespace="users")),
    url(
        r'^practitioners/',
        include('practitioners.urls', namespace="practitioners")),
    url(
        r'^patients/',
        include('patients.urls', namespace="patients")),
]
