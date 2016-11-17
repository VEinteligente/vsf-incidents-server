from django.conf.urls import include, url
import views


urlpatterns = [
    url(
        r'^generate-token/$',
        views.GenerateToken.as_view()
    ),
    url(
        r'^example/$',
        views.ExampleView.as_view()
    ),

]
