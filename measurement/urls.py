from .rest              import urls as api_url
from .front             import urls as front_url
from .                  import views
from django.conf.urls   import include, url

urlpatterns = [
    #url(r'^', include(front_url, namespace='measurement_front')), #DEPRECATED
    #url(r'^api/', include(api_url, namespace='measurement_api')), #DEPRECATED
    url(r'^', include(('measurement.front.urls','front_url'), namespace='measurement_front')),
    url(r'^api/', include(('measurement.rest.urls','api_url'), namespace='measurement_api')),
    url(
        r'^update-flags/$',
        views.UpdateFlagView.as_view(),
        name='update-flags'
    ),
    url(
        r'^luigi-update/$',
        views.LuigiUpdateFlagView.as_view(),
        name='luigi'
    ),
]
