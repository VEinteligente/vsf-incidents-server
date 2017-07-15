from django import forms
from django.db.models.expressions import RawSQL
from django.db.models import F, Count, Case, When, CharField, Q
from event.models import Event, Site, ISP, Target, SiteCategory
from measurement.models import Flag


class EventForm(forms.ModelForm):
    """EventForm: ModelForm of Event model"""

    open_ended = forms.BooleanField(widget=forms.CheckboxInput(),
                                    required=False)
    flags = forms.CharField(widget=forms.TextInput(attrs={'class': 'hidden'}),
                            required=True, label="")

    class Meta:
        model = Event
        fields = ['open_ended', 'identification', 'flags', 'type']

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

            for f in filter(None, flags):
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


class EventExtendForm(forms.ModelForm):
    TYPE_CHOICES = (
        ('MED', 'MED'),
        ('DNS', 'DNS'),
        ('TCP', 'TCP'),
        ('HTTP', 'HTTP')
    )
    open_ended = forms.BooleanField(widget=forms.CheckboxInput(),
                                    required=False)
    flags_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        label='Chance all Measurements type to:')

    class Meta:
        model = Event
        fields = ['open_ended', 'identification', 'isp', 'type']


class EventEvidenceForm(forms.ModelForm):
    """
    EventEvidenceForm: ModelForm of Event model adding url model attributes
    to create event target.
    This is used to create/update an event with external evidence
    """
    open_ended = forms.BooleanField(widget=forms.CheckboxInput(),
                                    required=False)

    flags = forms.CharField(widget=forms.TextInput(attrs={}),
                            required=False, label="")

    isp = forms.ModelChoiceField(queryset=ISP.objects.all(), required=False)

    start_date = forms.DateTimeField(required=False)

    target_url = forms.URLField(
        label="Target URL",
        required=False)
    target_ip = forms.GenericIPAddressField(
        label="Target IP",
        required=False)
    target_site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        empty_label="(Nothing)",
        label="Target Site",
        required=False)
    target_domain = forms.CharField(
        widget=forms.TextInput(),
        required=False,
        label="Target Domain"
    )

    target_type = forms.ChoiceField(
        choices=Target.TYPE,
        required=False,
        label="Target Type"
    )

    class Meta:
        model = Event
        exclude = [
            'draft',
            'target',
            'plugin_name'
        ]

    # def __init__(self, *args, **kwargs):
    #     super(EventEvidenceForm, self).__init__(*args, **kwargs)
    #     target_types = [(None, '----')]
    #     for target_type in Target.TYPE:
    #         target_types.append(target_type)
    #     self.fields['target_type'].choices = target_types

    def clean(self):
        '''Data from EventForm'''

        form_data = self.cleaned_data
        print form_data

        if form_data['target_type'] != "":
            if form_data['target_type'] == Target.DOMAIN and (
                form_data['target_domain'] == ""
            ):
                self.add_error('target_domain', 'Field Required')

            elif form_data['target_type'] == Target.URL and (
                form_data['target_url'] == ""
            ):
                self.add_error('target_url', 'Field Required')

            elif form_data['target_type'] == Target.IP and (
                form_data['target_ip'] == ""
            ):
                self.add_error('target_ip', 'Field Required')

        if form_data['flags'] == "":
            # Required fields when an event only with external evidence
            if form_data['start_date'] is None:
                self.add_error('start_date', 'Field Required')
            if form_data['isp'] == "":
                self.add_error('isp', 'Field Required')
            if form_data['public_evidence'] == "":
                self.add_error('public_evidence', 'Field Required')

            # Check end date or open ended event
            if form_data['open_ended'] is False and form_data['end_date'] is None:
                self.add_error(
                    None, 'An event must have an end date or be open_ended'
                )
                self.add_error('open_ended', '')
                self.add_error('end_date', '')

        else:

            flags = form_data['flags'].split('&')

            # Get flags from database with same target, isp
            # and type
            bd_flags = []

            for f in filter(None, flags):
                bd_flags += Flag.objects.filter(
                    uuid=f
                ).select_related(
                    'metric__probe__isp',
                    'metric__probe__region'
                ).annotate(
                    isp=Case(
                        default=F('metric__probe__isp__name'),
                        output_field=CharField()
                    ),
                    region=Case(
                        default=F('metric__probe__region__name'),
                        output_field=CharField()
                    ),
                )

            if bd_flags:

                # If not all flags are the same target, isp and type then
                # show an error.

                if not all(
                    map(
                        lambda f: f.target == bd_flags[0].target and f.isp == bd_flags[0].isp and f.region == bd_flags[0].region,
                        bd_flags[1:]
                    )
                ):

                    self.add_error(
                        None,
                        'Selected flags must have the same inputs, probe ISP and probe Region'
                    )

                if not all(
                    map(
                        lambda f: f.event is None or f.event.id == self.instance.id,
                        bd_flags[1:]
                    )
                ):

                    self.add_error(
                        None,
                        'One flag is already asociated to an event'
                    )


class SelectSiteForm(forms.ModelForm):

    target = forms.CharField(
        widget=forms.widgets.HiddenInput()
    )

    class Meta:
        model = Target
        fields = [
            'site',
        ]


class SiteCategoryForm(forms.ModelForm):
    class Meta:
        model = SiteCategory
        fields = ['name', 'description', 'abbreviation']


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'description', 'category']
