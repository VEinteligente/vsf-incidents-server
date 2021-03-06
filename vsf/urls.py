
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
from Case import urls as case_urls
from measurement import urls as measurement_urls
from plugins import urls as plugins_urls
from vsf_user import urls as user_urls
from plugins import urls as plugin_urls
from dashboard import urls as dashboard_urls
from dashboard.views import HomeView
from django.conf import settings
from django.conf.urls.static import static


import debug_toolbar

urlpatterns = [
          url(r'^$', HomeView.as_view(), name="home"),
          url(r'^admin/', admin.site.urls),

          url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

          url(r'^dashboard/', include(dashboard_urls, namespace='dashboard')),
          url(r'^events/', include(event_urls, namespace='events')),
          url(r'^cases/', include(case_urls, namespace='cases')),
          url(r'^measurements/', include(measurement_urls, namespace='measurements')),
          url(r'^custom-tests/', include(plugin_urls, namespace='custom-tests')),
          url(r'^users/', include(user_urls, namespace='users')),
          url(r'^plugins/', include(plugins_urls, namespace='plugins')),
          url(r'^debug/', include(debug_toolbar.urls))
      ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
      + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

