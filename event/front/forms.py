from django import forms
from event.models import Event
from measurement.models import Flag


class EventForm(forms.ModelForm):
    open_ended = forms.BooleanField(widget=forms.CheckboxInput(),
                                    required=False)
    flags = forms.CharField(widget=forms.TextInput(attrs={'class': 'hidden'}),
                            required=True, label="")

    class Meta:
        model = Event
        fields = ['open_ended', 'identification', 'flags']

    def clean(self):
        form_data = self.cleaned_data
        
        if self.is_valid():

            flags = form_data['flags'].split(' ')

            bd_flags = []

            for f in flags:
                split = f.split('/')
                bd_flags += Flag.objects.filter(medicion=split[0],
                                                target=split[1],
                                                isp=split[2],
                                                ip=split[3],
                                                type_med=split[4])

            if bd_flags:
                if not all(map(lambda f: f.target == bd_flags[0].target and f.isp == bd_flags[0].isp
                               and f.type_med == bd_flags[0].type_med, bd_flags[1:])):
                    self.add_error(None,
                                   'Selected measurements must have the same targets, types and ISP')

        else:
            self.add_error(None,
                       'The Event must have measurements and identification asociated')