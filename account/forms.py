from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, login, logout

from account.models import User
from exchange.models import Exchange, Currency, Pair

class DateInput(forms.DateInput):
	input_type = "date"



class UserLoginForm(forms.Form):
	email           = forms.CharField(label=_('Adresse Email'), widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True)

	password        = forms.CharField(label=_('Mot de passe'), widget=forms.PasswordInput(attrs={
		'class': 'form-control'
	}))

	def clean(self):
		username = self.cleaned_data.get('email')
		password = self.cleaned_data.get('password')
		user = authenticate(username=username, password=password)
		if not user or not user.is_active:
			raise forms.ValidationError(_('Désolé, ces identifiants sont incorrects'))
		return self.cleaned_data

	def login(self, request):
		username = self.cleaned_data.get('email')
		password = self.cleaned_data.get('password')
		user = authenticate(username=username, password=password)
		return user



class CustomUserCreationForm(UserCreationForm):

	email = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Adresse email'), label_suffix='*:')

	first_name = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Prénom'), label_suffix='*:')

	last_name = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Nom de famille'), label_suffix='*:')

	password1 = forms.CharField(widget=forms.PasswordInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Mot de passe'), label_suffix='*:')

	password2 = forms.CharField(widget=forms.PasswordInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Mot de passe (vérification)'), label_suffix='*:')

	class Meta:
		model = User
		fields = ["email", "first_name", "last_name", "password1", "password2"]
	


# class TradingScreenForm(forms.ModelForm):
# 	class Meta:
# 		model = Exchange
# 		fields = ['user','exchange_api','allowed_pairs']


