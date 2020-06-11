from django.conf.urls import include, url
#from rest import urls as api_url    DEPRECATED
#from front import urls as front_url DEPRECATED

urlpatterns = [
    url(r'^', include(('Case.front.urls', 'front'), namespace='case_front')),
    url(r'^api/', include(('Case.rest.urls','rest'), namespace='case_api')),
]


#urlpatterns = [
#    url(r'^', include(front_url, namespace='case_front')),
#    url(r'^api/', include(api_url, namespace='case_api')),
#]
