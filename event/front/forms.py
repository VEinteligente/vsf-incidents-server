from django import forms
from event.models import Event
from measurement.models import Flag


class EventForm(forms.ModelForm):
    """EventForm: ModelForm of Event model"""

    open_ended = forms.BooleanField(widget=forms.CheckboxInput(),
                                    required=False)
    flags = forms.CharField(widget=forms.TextInput(attrs={'class': 'hidden'}),
                            required=True, label="")

    class Meta:
        model = Event
        fields = ['open_ended', 'identification', 'flags']

    def clean(self):
        '''Data from EventForm'''

        form_data = self.cleaned_data

        # If form is valid then check if flags are the same
        # target, isp and type. Otherwise, show a not valid
        # form error.

        if self.is_valid():

            # Format flags from the form.

            flags = form_data['flags'].split(' ')

            bd_flags = []

            # Get flags from database with same target, isp
            # and type

            for f in flags:
                split = f.split('&')
                bd_flags += Flag.objects.filter(medicion=split[0],
                                                target__url=split[1],
                                                isp=split[2],
                                                ip=split[3],
                                                type_med=split[4])

            if bd_flags:

                # If not all flags are the same target, isp and type then
                # show an error.

                if not all(map(lambda f: f.target == bd_flags[0].target and f.isp == bd_flags[0].isp
                               and f.type_med == bd_flags[0].type_med, bd_flags[1:])):
                    self.add_error(None,
                                   'Selected measurements must have the same targets, types and ISP')

        else:
            self.add_error(None,
                       'The Event must have measurements and identification asociated')