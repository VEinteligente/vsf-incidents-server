from django.conf.urls import include, url
from vsf_user.front import views


urlpatterns = [
    url(
        r'^list-apikey/$',
        views.ListAPIUsers.as_view(),
        name='api-users-list'
    ),
    url(
        r'^list-apikey-ajax/$',
        views.APIUsersDataTableAjax.as_view(),
    ),
    url(
        r'^(?P<user_id>[0-9]+)/delete-apikey/$',
        views.DeleteAPIUsers.as_view(),
        name='api-users-delete'
    ),

]
