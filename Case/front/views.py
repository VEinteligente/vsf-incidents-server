from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from datetime import date
from .forms import CaseForm, UpdateForm, UpdateFormSet, CategoryForm
from Case.models import Case, Update, Category
from event.models import Event

from dashboard.mixins import PageTitleMixin
from django.core.urlresolvers import reverse_lazy


class ListCase(LoginRequiredMixin, PageTitleMixin, generic.ListView):
    """ListCase: ListView than
    display a list of all cases"""
    model = Case
    template_name = "list_case.html"
    context_object_name = "cases"
    page_header = "Cases"
    page_header_description = "List of cases"
    breadcrumb = ["Cases"]


class CreateCase(LoginRequiredMixin, PageTitleMixin, generic.CreateView):
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
        if form.cleaned_data['end_date'] is None and form.cleaned_data['open_ended'] is False:
            form.add_error(None, 'You must give an end date to this case or select open ended')
            form.add_error('end_date', '')
            form.add_error('open_ended', '')
            return self.form_invalid(form)

        self.object = form.save(commit=False)

        events_ids = form.cleaned_data['events'].split(',')
        events = []
        if (str(events_ids[0]) != ''):
            events = Event.objects.filter(id__in=events_ids)

        self.object.save()
        for event in events:
            self.object.events.add(event)

        msg = 'Se ha creado el caso'

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


class CreateCaseFromEventsView(CreateCase):
    model = Case
    template_name = 'list_events_create_case.html'
    page_header_description = "Select the event(s) to associate as a New Case"


class DetailCase(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    """DetailCase: DetailView than
    give the details of a specific Case object"""
    model = Case
    context_object_name = "case"
    template_name = "detail_case.html"
    page_header = "Case Details"
    page_header_description = ""
    breadcrumb = ["Cases", "Case Details"]


class ChangeCaseStatus(LoginRequiredMixin, generic.UpdateView):
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
    """ChangeCaseStatusDetail: UpdateView extension of ChangeCaseStatus 
    than change case status from detail case page.
    It can be Publish or Sketch. Sketch for default"""
    def set_success_url(self, id):
        self.success_url = reverse_lazy(
            'cases:case_front:detail-case', kwargs={'pk': id})


class DeleteCase(LoginRequiredMixin, generic.DeleteView):
    """DeleteCase: DeleteView than delete an specific case."""
    model = Case
    success_url = reverse_lazy('cases:case_front:list-case')


class UpdateCase(LoginRequiredMixin, PageTitleMixin, generic.UpdateView):
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

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()
        form_class = self.get_form_class()
        # get case form
        form = self.get_form(form_class)
        # get update formset
        update_forms = UpdateFormSet(instance=self.object)

        # must pass form and update formset to context
        return self.render_to_response(
            self.get_context_data(form=form,
                                  update_form=update_forms))

    def get_context_data(self, **kwargs):

        context = super(UpdateCase, self).get_context_data(**kwargs)
        events = Event.objects.filter(draft=False)
        context['events'] = events
        # context['update_form'] = UpdateFormSet(instance=self.object)
        # Initial data for the form

        return context

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        update_forms = UpdateFormSet(self.request.POST, instance=self.object)

        if (form.is_valid() and update_forms.is_valid()):
            return self.form_valid(form, update_forms)
        else:
            return self.form_invalid(form, update_forms)

    def form_valid(self, form, update_forms):
        # first save case data in form
        if form.cleaned_data['end_date'] is None and form.cleaned_data['open_ended'] is False:
            form.add_error(None, 'You must give an end date to this case or select open ended')
            form.add_error('end_date', '')
            form.add_error('open_ended', '')
            return self.form_invalid(form, update_forms)

        self.object = form.save(commit=False)
        events_ids = form.cleaned_data['events'].split(',')
        events = []
        if (str(events_ids[0]) != ''):
            events = Event.objects.filter(id__in=events_ids)

        self.object.save()
        self.object.events.clear()
        for event in events:
            self.object.events.add(event)

        # Save every posible update in update_forms
        user = None
        if self.request.user.is_authenticated():
            user = self.request.user

        updates = update_forms.save(commit=False)
        for obj in update_forms.deleted_objects:
            obj.delete()

        for update in updates:
            update.created_by = user
            update.created = date.today()
            update.save()

        # Success message
        msg = 'Case modified successfully'

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, update_forms):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  update_form=update_forms))

    def get_form(self, form_class=None):
        form = super(UpdateCase, self).get_form(form_class)
        if not self.object.end_date:
            form.fields['open_ended'].initial = True
        return form


class CreateUpdate(LoginRequiredMixin, PageTitleMixin, generic.CreateView):
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


class UpdateUpdate(LoginRequiredMixin, PageTitleMixin, generic.UpdateView):
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


class DeleteUpdate(LoginRequiredMixin, generic.DeleteView):
    """DeleteUpdate: DeleteView than
    delete an update of a specific case"""
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


class ListCategory(PageTitleMixin, generic.ListView):
    model = Category
    template_name = "list_category.html"
    context_object_name = "categories"
    page_header = "Categories"
    page_header_description = "List of categories"
    breadcrumb = ["Cases", "Categories"]


class CreateCategory(PageTitleMixin, generic.CreateView):
    """CreateCategory: CreateView than
    create a new Category object in DB"""
    form_class = CategoryForm
    page_header = "New Category"
    page_header_description = ""
    breadcrumb = ["Cases", "Categories", "New Category"]
    success_url = reverse_lazy('cases:case_front:list-category')
    template_name = 'create_category.html'


class UpdateCategory(PageTitleMixin, generic.UpdateView):
    """UpdateCase: UpdateView than
    update an Case object in DB"""
    form_class = CategoryForm
    context_object_name = 'category'
    page_header = "Edit Category"
    page_header_description = ""
    model = Category
    breadcrumb = ["Cases", "Categories", "Edit Category"]
    success_url = reverse_lazy('cases:case_front:list-category')
    template_name = 'create_category.html'


class DeleteCategory(generic.DeleteView):
    model = Category
    success_url = reverse_lazy('cases:case_front:list-category')
