from django import forms
from .models import User
from django.core.exceptions import ValidationError
from datetime import date
import re

class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        if age < 18:
            raise forms.ValidationError('You must be at least 18 years old to register.')
        return date_of_birth

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r'^[a-zA-Z0-9]+@(gmail\.com|outlook\.(com|in))$', email):
            raise forms.ValidationError('Invalid email address. Only Gmail and Outlook addresses are allowed.')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return confirm_password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) > 12:
            raise forms.ValidationError('Username must be at most 8 characters long.')
        if not any(char.isdigit() for char in username) or not any(char.isalpha() for char in username):
            raise ValidationError('Username must contain both letters and numerics.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already in use.')
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) > 8:
            raise forms.ValidationError('First name must be at most 8 characters long.')
        if not first_name.isalpha():
            raise forms.ValidationError('First name must contain only alphabetic characters.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) > 8:
            raise forms.ValidationError('Last name must be at most 8 characters long.')
        if not last_name.isalpha():
            raise forms.ValidationError('Last name must contain only alphabetic characters.')
        return last_name

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'date_of_birth', 'password']
        widgets = {
            'password': forms.PasswordInput,
        }


class ChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class VoterLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
