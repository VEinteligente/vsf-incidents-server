from django.conf.urls import include, url
from .demo import urls as demo_url

urlpatterns = [
    url(r'^demo/', include(('plugins.demo.urls','demo_url'), namespace='demo')),
]
