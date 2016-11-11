from django import forms
from event.models import Event
from measurement.models import Flag


class EventForm(forms.ModelForm):
    open_ended = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    flags = forms.CharField(widget=forms.TextInput(attrs={'class': 'hidden'}), required=True, label="")

    class Meta:
        model = Event
        fields = ['open_ended', 'identification', 'flags']

    def clean(self):
        form_data = self.cleaned_data
        flags = form_data['flags'].split(' ')
        flags = Flag.objects.filter(medicion__in=flags)

        if flags:
            if flags.exclude(target=flags[0].target, isp=flags[0].isp, type_med=flags[0].type_med):
                self.add_error(None, 'Selected measurements must have the same targets, types and ISP')
