from django import forms
from django.forms.models import inlineformset_factory
from django.forms import DateTimeField
from Case.models import Case, Update, Category


class CaseForm(forms.ModelForm):
    open_ended = forms.BooleanField(widget=forms.CheckboxInput(),
                                    required=False)
    events = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'hidden'}), required=False, label="")

    start_date = DateTimeField(
        widget=forms.widgets.DateTimeInput(
            format='%m/%d/%Y'))

    end_date = DateTimeField(
        widget=forms.widgets.DateTimeInput(
            format='%m/%d/%Y'),
        required=False)

    class Meta:
        model = Case
        fields = [
            'title', 'description', 'start_date', 'end_date',
            'category', 'open_ended', 'draft', 'events'
        ]


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = [
            'name', 'display_name'
        ]


class UpdateForm(forms.ModelForm):
    # date = forms.DateField(widget=forms.TextInput(
    #     attrs={'class': 'update_date'}),
    #     required=True)
    date = DateTimeField(
        widget=forms.widgets.DateTimeInput(
            format='%m/%d/%Y',
            attrs={'class': 'update_date'}))

    class Meta:
        model = Update
        fields = ['title', 'text', 'category', 'date']


UpdateFormSet = inlineformset_factory(
    Case,
    Update,
    form=UpdateForm,
    extra=0,
    can_delete=True
)
