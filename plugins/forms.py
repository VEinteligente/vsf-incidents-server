from django import forms


class DataTableRangePicker(forms.Form):
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)