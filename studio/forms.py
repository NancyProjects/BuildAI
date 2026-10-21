from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Project
class SignupForm(UserCreationForm):
 email=forms.EmailField(required=True)
 class Meta(UserCreationForm.Meta):model=User;fields=('username','email','password1','password2')
 def clean_email(self):
  email=self.cleaned_data['email'].strip().lower()
  if User.objects.filter(email__iexact=email).exists():raise forms.ValidationError('This email is already registered.')
  return email
class ProjectForm(forms.ModelForm):
 class Meta:model=Project;fields=('title','description')
