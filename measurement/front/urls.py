from django.conf.urls import include, url
from measurement.front import views


urlpatterns = [
    url(
        r'^$', views.LoginPrueba.as_view(), name='index'
    ),
]
