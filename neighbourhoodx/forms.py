from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Administrator, Neighbourhood, SOCIAL_SERVICES, Member, Post, Business

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
