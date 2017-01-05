from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):

    login = forms.CharField(max_length=100, required=True)
    password = forms.PasswordInput()


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = (
            'last_login',
            'is_superuser', 
            'groups',
            'user_permissions',
            'is_staff',
            'is_active',
            'date_joined'
        )

    def save(self, commit=True):
        """
        Save this form's self.instance object if commit=True. Otherwise, add
        a save_m2m() method to the form which can be called after the instance
        is saved manually at a later time. Return the model instance.
        """
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        else:
            # If not committing, add a method to the form to allow deferred
            # saving of m2m data.
            self.save_m2m = self._save_m2m
        return self.instance
