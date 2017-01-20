import json
from datetime import datetime
from django.http import JsonResponse
from eztables.views import DatatablesView
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
from django.views import generic

from vsf_user.models import TokenControl
from froms import ApiUserForm


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class ListAPIUsers(LoginRequiredMixin, AjaxableResponseMixin, generic.CreateView):
    model = User
    form_class = ApiUserForm
    template_name = 'list_api_user.html'
    success_url = 'http://google.com'

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = User.objects.create_user(
            form.cleaned_data['username'],
            form.cleaned_data['email'],
            form.cleaned_data['password']
        )

        self.object.first_name = form.cleaned_data['first_name']
        self.object.last_name = form.cleaned_data['last_name']
        self.object.save()

        g = Group.objects.get(name='api')
        token = Token.objects.create(user=self.object)
        TokenControl.objects.create(token=token, last_used=datetime.now())
        g.user_set.add(self.object)

        data = {
            'pk': self.object.pk,
        }
        return JsonResponse(data)


class APIUsersDataTableAjax(LoginRequiredMixin, DatatablesView):

    queryset = Token.objects.all()
    fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'user_id')

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder)
        )


class DeleteAPIUsers(LoginRequiredMixin, AjaxableResponseMixin, generic.DeleteView):
    model = User
    pk_url_kwarg = 'user_id'
    template_name = 'list_api_user.html'
    success_url = 'http://google.com'

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'ok'})
