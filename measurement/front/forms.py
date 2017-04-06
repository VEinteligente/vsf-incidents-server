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


class ManualFlagForm(forms.Form):

    metrics = forms.CharField(widget=forms.TextInput(attrs={'class': 'hidden', 'required': False}),
                              label="")


class MeasurementToEventForm(ManualFlagForm):

    metric_ip = forms.CharField(widget=forms.TextInput(attrs={'class': 'hidden', 'required': False}),
                                label="")