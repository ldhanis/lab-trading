from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.widgets import FilteredSelectMultiple

from account.models import TradingScreen, User
from exchange.models import Currency, ExchangeApi, Pair

from django_select2 import forms as s2forms

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
	
class BaseAutocompleteSelect(s2forms.ModelSelect2Widget):
    class Media:
        js = ("admin/js/vendor/jquery/jquery.min.js",)

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.attrs = {"style": "width: 300px"}

    def build_attrs(self, base_attrs, extra_attrs=None):
        base_attrs = super().build_attrs(base_attrs, extra_attrs)
        base_attrs.update(
            {"data-minimum-input-length": 0, "data-placeholder": self.empty_label}
        )
        return base_attrs

class TradingScreenForm(forms.ModelForm):
	user = forms.ModelChoiceField(required = True, 
	queryset = User.objects.all(), 
	label=_('user'), label_suffix='*:', 
	widget=forms.Select(attrs={'class':'form-control'}))

	allowed_pairs = forms.ModelChoiceField(
        queryset=Pair.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Multis',
		is_stacked=False, 
		attrs={'class':'form-control'}),
		label=_('Allowed Pairs'), 
		label_suffix='*:',
    )
	exchange_api 	= forms.ModelChoiceField(required = True, 
	queryset = ExchangeApi.objects.all(), 
	label=_('Exchange API'), label_suffix='*:', 
	widget=forms.Select(attrs={'class':'form-control'}))

	
	class Meta:
		model = TradingScreen
		fields = ['user','exchange_api','allowed_pairs']


