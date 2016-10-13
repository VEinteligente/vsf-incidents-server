"""vsf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from event import urls as event_urls
from incident import urls as incident_urls
from measurement import urls as measurement_urls
from vsf_user import urls as user_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^events/', include(event_urls, namespace='events')),
    url(r'^incidents/', include(incident_urls, namespace='incidents')),
    url(r'^measurements/', include(measurement_urls, namespace='measurements')),
    url(r'^users/', include(user_urls, namespace='users')),
]
