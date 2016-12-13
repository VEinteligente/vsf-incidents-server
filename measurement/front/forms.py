from django import forms
from measurement.models import MutedInput, Probe


class MutedInputForm(forms.ModelForm):

    class Meta:
        model = MutedInput
        fields = ['url', 'type_med']


class ProbeForm(forms.ModelForm):

    class Meta:
        model = Probe
        fields = ['identification', 'region', 'country', 'city', 
                  'isp', 'plan']
