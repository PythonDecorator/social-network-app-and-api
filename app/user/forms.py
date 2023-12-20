"""
Forms for the user views
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "First Name", "class": "form-control"}))
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "Last Name", "class": "form-control"}))

    email = forms.EmailField(widget=forms.EmailInput(
        attrs={
            "placeholder": "Email",
            "class": "form-control"
        }
    ))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "placeholder": "Password",
            "class": "form-control"
        }
    ))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "placeholder": "Password check",
            "class": "form-control"
        }
    ))

    username = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "Username", "class": "form-control"}))

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'username')


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "First Name", "class": "form-control"}))
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "Last Name", "class": "form-control"}))

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name')
