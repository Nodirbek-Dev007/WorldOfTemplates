from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms

from .models import *

class ProfileInput(ModelForm):
  image = forms.ImageField(widget=forms.FileInput())
  class Meta:
    model = Customer
    fields = '__all__'
    exclude = ['user', 'email']
    widgets = {
      'image': forms.ClearableFileInput(attrs={'class': 'custom-file-input'}),
    }

class CreateUserForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    widgets = {
      'username': forms.TextInput(attrs={'placeholder': 'Enter username'}),
      'first_name': forms.TextInput(attrs={'placeholder': 'Enter first name'}),
      'last_name': forms.TextInput(attrs={'placeholder': 'Enter last name'}),
      'email': forms.EmailInput(attrs={'placeholder': 'Enter email'}),
      'password1': forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
      'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
    }

  def __init__(self, *args, **kwargs):
    super(CreateUserForm, self).__init__(*args, **kwargs)

    self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
    self.fields['first_name'].widget.attrs.update({'placeholder': 'First name'})
    self.fields['last_name'].widget.attrs.update({'placeholder': 'Last name'})
    self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
    self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
    self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})
