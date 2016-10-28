from django.conf.urls import include, url
from rest import urls as api_url
from front import urls as front_url
import views

urlpatterns = [
    url(r'^', include(front_url, namespace='measurement_front')),
    url(r'^api/', include(api_url, namespace='measurement_api')),
    url(
        r'^update-flags/$',
        views.UpdateFlagView.as_view(),
        name='update-flags'
    ),
]
