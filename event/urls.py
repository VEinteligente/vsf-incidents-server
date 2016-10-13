from django.conf.urls import include, url
from rest import urls as api_url
from front import urls as front_url

urlpatterns = [
    url(r'^', include(front_url, namespace='event_front')),
    url(r'^api/', include(api_url, namespace='event_api')),
]
