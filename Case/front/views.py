from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect

from .forms import CaseForm
from Case.models import Case
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

        if not form.cleaned_data['open_ended']:
            self.object.end_date = events.latest('end_date').date

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
    template_name = 'list_event.html'
    success_url = reverse_lazy('cases:case_front:list-case')
