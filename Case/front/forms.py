from django import forms
from Case.models import Case, Update


class CaseForm(forms.ModelForm):
    open_ended = forms.BooleanField(widget=forms.CheckboxInput(),
                                    required=False)
    events = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'hidden'}), required=False, label="")

    class Meta:
        model = Case
        fields = [
            'title', 'description', 'start_date', 'end_date',
            'category', 'open_ended', 'draft', 'events'
        ]


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ['title', 'text', 'category', 'date']
