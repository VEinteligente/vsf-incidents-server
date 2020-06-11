from django.conf.urls import include, url
from  .rest import urls as api_url
from .front import urls as front_url


urlpatterns = [
    url(r'^', include(('event.front.urls', 'front'), namespace='event_front')),
    url(r'^api/', include(('event.rest.urls','rest'), namespace='event_api')),
]

#urlpatterns = [
#    url(r'^', include(front_url, namespace='event_front')),
#    url(r'^api/', include(api_url, namespace='event_api')),
#]
