from django.conf.urls import include, url
from vsf_user.front import views


urlpatterns = [
    url(
        r'^$',
        views.LoginPrueba.as_view(),
    ),

]
