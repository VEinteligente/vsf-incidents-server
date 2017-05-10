from django.conf.urls import include, url
from demo import urls as demo_url
from dns import urls as dns_urls
from tcp import urls as tcp_urls
from http import urls as http_urls
from ndt import urls as ndt_urls

import views

urlpatterns = [

    url(
        r'^suggested-events-ajax/$',
        views.SuggestedEventsAjax.as_view(),
        name='suggested-events-ajax'
    ),

    url(r'^demo/', include(demo_url, namespace='demo')),
    url(r'^dns/', include(dns_urls, namespace='dns')),
    url(r'^tcp/', include(tcp_urls, namespace='tcp')),
    url(r'^http/', include(http_urls, namespace='http')),
    url(r'^ndt/', include(ndt_urls, namespace='ndt')),
]
