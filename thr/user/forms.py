from django import forms
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    affiliation = forms.CharField(max_length=100, help_text='affiliation')

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields  # + ('email', 'first_name', 'last_name', 'affiliation')
