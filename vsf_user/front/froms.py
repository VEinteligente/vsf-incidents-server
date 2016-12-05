from django import forms


class LoginForm(forms.Form):

    login = forms.CharField(max_length=100, required=True)
    password = forms.PasswordInput()
