from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth import forms


urlpatterns = [
    url(
        '^login/$', auth_views.login,
        {
            'template_name': 'users_auth/login.html'
        },
        name='login'
    ),
    url(
        '^logout/$', auth_views.logout,
        {
            'next_page': 'dashboard:login'
        },
        name='logout'
    ),
    url(
        '^password-change/$',
        auth_views.password_change,
        {
            'template_name': 'users_auth/password_change_form.html',
            'post_change_redirect': 'dashboard:password_change_done',
            'password_change_form': forms.PasswordChangeForm
        },
        name='password_change'
    ),
    url(
        '^password-change/done/$',
        auth_views.password_change_done,
        {
            'template_name': 'users_auth/password_change_done.html',
            'extra_context': {
                'title': 'Modificaci&oacute;n de contrase&ntilde;a exitosa.'
            }
        },
        name='password_change_done'
    ),
    url(
        '^password-reset/request/$',
        auth_views.password_reset,
        {
            'template_name': 'users_auth/password_reset_form.html',
            'password_reset_form': forms.PasswordResetForm,
            'post_reset_redirect': 'dashboard:password_reset_done',
            'email_template_name': 'users_auth/emails/'
                                   'password_reset_email.html',
            'html_email_template_name': 'users_auth/emails/'
                                        'password_reset_email.html',
            'subject_template_name':  'users_auth/emails/'
                                      'password_reset_subject.txt',
        },
        name='password_reset'
    ),
    url(
        '^password-reset/request/done/$',
        auth_views.password_reset_done,
        {
            'template_name': 'users_auth/password_reset_done.html',
        },
        name='password_reset_done'
    ),
    url(
        '^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {
            'template_name': 'users_auth/password_reset_confirm.html',
            'set_password_form': forms.SetPasswordForm,
            'post_reset_redirect': 'dashboard:password_reset_complete',
            'extra_context': {
                'title': 'Modificaci&oacute;n de contrase&ntilde;a exitosa.'
            }
        },
        name='password_reset_confirm'
    ),
    url(
        '^password-reset/complete/$',
        auth_views.password_reset_complete,
        {
            'template_name': 'users_auth/password_reset_complete.html',
        },
        name='password_reset_complete'
    ),
]
