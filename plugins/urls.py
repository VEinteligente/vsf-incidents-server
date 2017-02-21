from django.conf.urls import include, url
from demo import urls as demo_url
from ndt import urls as ndt_urls

urlpatterns = [
    url(r'^demo/', include(demo_url, namespace='demo')),
    url(r'^ndt/', include(ndt_urls, namespace='ndt')),
]
