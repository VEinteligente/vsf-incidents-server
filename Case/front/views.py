from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect

from datetime import date
from .forms import CaseForm, UpdateForm
from Case.models import Case, Update
from event.models import Event

from dashboard.mixins import PageTitleMixin
from django.core.urlresolvers import reverse_lazy


class ListCase(PageTitleMixin, generic.ListView):
    """ListCase: ListView than
    display a list of all cases"""
    model = Case
    template_name = "list_case.html"
    context_object_name = "cases"
    page_header = "Cases"
    page_header_description = "List of cases"
    breadcrumb = ["Cases"]


class CreateCase(PageTitleMixin, generic.CreateView):
    """CreateCase: CreateView than
    create a new Case object in DB"""
    form_class = CaseForm
    page_header = "New Case"
    page_header_description = ""
    breadcrumb = ["Cases", "New Case"]
    success_url = reverse_lazy('cases:case_front:list-case')
    template_name = 'create_case.html'

    def get_context_data(self, **kwargs):
        events = Event.objects.filter(draft=False)
        kwargs['events'] = events
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CreateCase, self).get_context_data(**kwargs)

    def form_valid(self, form):

        self.object = form.save(commit=False)

        events = form.cleaned_data['events'].split(',')
        events = Event.objects.filter(id__in=events)

        self.object.save()
        for event in events:
            self.object.events.add(event)

        msg = 'Se ha creado el caso'

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


class DetailCase(PageTitleMixin, generic.DetailView):
    """DetailCase: DetailView than
    give the details of a specific Case object"""
    model = Case
    context_object_name = "case"
    template_name = "detail_case.html"
    page_header = "Case Details"
    page_header_description = ""
    breadcrumb = ["Cases", "Case Details"]


class ChangeCaseStatus(generic.UpdateView):
    """ChangeEventStatus: UpdateView than change case status.
    It can be Publish or Sketch. Sketch for default"""
    model = Case
    success_url = None

    def get(self, request, *args, **kwargs):
        case = self.model.objects.get(id=kwargs['pk'])
        if case.draft:
            case.draft = False
            msg = u'Se ha actualizado el estado del caso a Publico'
        else:
            case.draft = True
            msg = u'Se ha actualizado el estado del caso a Borrador'

        case.save(update_fields=['draft'])
        self.set_success_url(case.id)

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.success_url)

    def set_success_url(self, id):
        self.success_url = reverse_lazy('cases:case_front:list-case')


class ChangeCaseStatusDetail(ChangeCaseStatus):
    def set_success_url(self, id):
        self.success_url = reverse_lazy(
            'cases:case_front:detail-case', kwargs={'pk': id})


class DeleteCase(generic.DeleteView):
    """DeleteCase: DeleteView than delete an specific case."""
    model = Case
    success_url = reverse_lazy('cases:case_front:list-case')


class UpdateCase(PageTitleMixin, generic.UpdateView):
    """UpdateCase: UpdateView than
    update an Case object in DB"""
    form_class = CaseForm
    context_object_name = 'case'
    page_header = "Update Case"
    page_header_description = ""
    breadcrumb = ["Cases", "Edit Case"]
    model = Case
    success_url = reverse_lazy('cases:case_front:list-case')
    template_name = 'create_case.html'

    def get_context_data(self, **kwargs):

        context = super(UpdateCase, self).get_context_data(**kwargs)
        events = Event.objects.filter(draft=False)
        context['events'] = events

        # Initial data for the form

        return context

    def form_valid(self, form):

        self.object = form.save(commit=False)

        events = form.cleaned_data['events'].split(',')
        events = Event.objects.filter(id__in=events)

        self.object.save()
        for event in events:
            self.object.events.add(event)

        msg = 'Se ha editado el caso'

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class=None):
        form = super(UpdateCase, self).get_form(form_class)
        if not self.object.end_date:
            form.fields['open_ended'].initial = True
        return form


class CreateUpdate(PageTitleMixin, generic.CreateView):
    """CreateUpdate: CreateView than
    create a new Update object to a specific Case"""
    form_class = UpdateForm
    page_header = ""
    page_header_description = ""
    breadcrumb = ["Cases", "New Update"]
    success_url = reverse_lazy('cases:case_front:list-case')
    template_name = 'create_update.html'

    def get_context_data(self, **kwargs):
        case = Case.objects.get(pk=self.kwargs.get('pk', None))
        self.page_header = "New Update for Case: " + str(case.title)
        kwargs['case'] = case
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CreateUpdate, self).get_context_data(**kwargs)

    def form_valid(self, form):

        self.object = form.save(commit=False)

        case = Case.objects.get(pk=self.kwargs.get('pk', None))
        self.object.case = case
        user = None
        if self.request.user.is_authenticated():
            user = self.request.user
        self.object.created_by = user
        self.object.save()

        msg = 'Se ha creado el update al caso'

        messages.success(self.request, msg)
        self.success_url = reverse_lazy(
            'cases:case_front:detail-case', kwargs={'pk': case.id})

        return HttpResponseRedirect(self.get_success_url())


class UpdateUpdate(PageTitleMixin, generic.UpdateView):
    """UpdateUpdate: UpdateView than
    update an update of a specific case"""
    form_class = UpdateForm
    context_object_name = 'update'
    page_header = "Edit Update"
    page_header_description = ""
    breadcrumb = ["Cases", "Edit Update"]
    model = Update
    success_url = reverse_lazy('cases:case_front:list-case')
    template_name = 'create_update.html'

    def get_context_data(self, **kwargs):
        self.page_header = "Edit Update in Case: " + str(self.object.case.title)
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(UpdateUpdate, self).get_context_data(**kwargs)

    def form_valid(self, form):

        self.object = form.save(commit=False)
        user = None
        if self.request.user.is_authenticated():
            user = self.request.user
        self.object.created_by = user
        self.object.created = date.today()
        self.object.save()

        msg = 'Se ha editado el update'

        messages.success(self.request, msg)
        self.success_url = reverse_lazy(
            'cases:case_front:detail-case', kwargs={'pk': self.object.case.id})

        return HttpResponseRedirect(self.get_success_url())


class DeleteUpdate(generic.DeleteView):
    model = Update
    success_url = reverse_lazy('cases:case_front:list-case')

    def delete(self, request, *args, **kwargs):

        update = self.get_object()

        self.success_url = reverse_lazy(
            'cases:case_front:detail-case', kwargs={'pk': update.case.id})
        update.delete()

        msg = 'Se ha eliminado el update elegido'

        messages.success(request, msg)

        return HttpResponseRedirect(self.success_url)
