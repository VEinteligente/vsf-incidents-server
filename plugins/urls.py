from django.conf.urls import include, url
from demo import urls as demo_url
import views

urlpatterns = [
    url(r'^demo/', include(demo_url, namespace='demo')),
    url(
        r'^test/$',
        views.test.as_view(),
        name='test'
    ),
]