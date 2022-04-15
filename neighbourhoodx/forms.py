from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Administrator, Neighbourhood, SocialServices, Member, Post, Business

class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class AdministratorForm(forms.ModelForm):
    """Form definition for Administrator."""

    class Meta:
        """Meta definition for Administratorform."""

        model = Administrator
        fields = '__all__'
        exclude = ['user',]

class NeighbourhoodForm(forms.ModelForm):
    """Form definition for Neighbourhood."""

    class Meta:
        """Meta definition for Neighbourhoodform."""

        model = Neighbourhood
        fields = '__all__'
        exclude = ['admin', 'occupants']

class AddResidentForm(forms.Form):
    name = forms.CharField(label='Resident name', max_length=50)
    username = forms.CharField(label='Username', max_length=50)
    email = forms.EmailField()

class SocialServicesForm(forms.ModelForm):
    """Form definition for SocialServices."""

    class Meta:
        """Meta definition for SocialServicesform."""

        model = SocialServices
        fields = '__all__'
        exclude = ['neighbourhood']

class PostForm(forms.ModelForm):
    """Form definition for Post."""

    class Meta:
        """Meta definition for Postform."""

        model = Post
        fields = ['body']

class BusinessForm(forms.ModelForm):
    """Form definition for Business."""

    class Meta:
        """Meta definition for Businessform."""

        model = Business
        fields = '__all__'
        exclude = ['neighbourhood', 'owner']






