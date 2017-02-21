from django.conf.urls import include, url
import views

urlpatterns = [
    url(
        r'^test/$',
        views.PuraPrueba.as_view(),
        name='nam'
    ),
    # url(
    #     r'^demo-ajax/$',
    #     views.DemoAjaxView.as_view(),
    #     name='demo-ajax'
    # ),
]
