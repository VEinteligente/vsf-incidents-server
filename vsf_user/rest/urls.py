from django.conf.urls import include, url
import views


urlpatterns = [
    url(
        r'^retrieve-apiuser/(?P<user_id>[0-9]+)/$',
        views.DetailApiKeyUser.as_view()
    ),
    url(
        r'^generate-token/$',
        views.GenerateToken.as_view()
    ),
    url(
        r'^example/$',
        views.ExampleView.as_view()
    ),

]
