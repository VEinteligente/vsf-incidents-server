from django.conf.urls import include, url
import views

urlpatterns = [
    url(
        r'^test/$',
        views.test.as_view(),
        name='test'
    ),
]