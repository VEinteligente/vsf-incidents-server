from django.conf.urls import include, url
from rest import urls as api_url
from front import urls as front_url

urlpatterns = [
    url(r'^', include(front_url, namespace='case_front')),
    url(r'^api/', include(api_url, namespace='case_api')),
]
