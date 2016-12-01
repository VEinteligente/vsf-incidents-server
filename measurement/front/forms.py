from django import forms
from measurement.models import MutedInput


class MutedInputForm(forms.ModelForm):

    class Meta:
        model = MutedInput
        fields = ['url', 'type_med']
