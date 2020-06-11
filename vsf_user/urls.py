from django.conf.urls import include, url
from .rest import urls as api_url
from .front import urls as front_url

urlpatterns = [
    url(r'^', include(('vsf_user.front.urls','front_url'), namespace='user_front')),
    url(r'^api/', include(('vsf_user.rest.urls','api_url'), namespace='user_api')),
]

