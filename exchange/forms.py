from django import forms
from django.utils.translation import gettext_lazy as _

from exchange.models import Exchange, Currency, Pair, ExchangeApi

class ExchangeForm(forms.ModelForm):

	name = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Nom'), label_suffix='*:')

	class Meta:
		model = Exchange
		fields = ['name']

class ExchangeApiForm(forms.ModelForm):

    exchangeName = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_(''), label_suffix='*:')

    class Meta:
        model = ExchangeApi
        fields = []

class CurrencyForm(forms.ModelForm):
	
	name = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Name'), label_suffix='*:')

	# symbol = forms.CharField(widget=forms.TextInput(attrs={
	# 	'class': 'form-control'
	# }), required=True, label=_('Symbol'), label_suffix='*:')

	class Meta:
		model = Currency
		fields = ['name']

class PairForm(forms.ModelForm):

	symbol = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Symbol'), label_suffix='*:')

	class Meta:
		model = Pair
		fields = ['symbol']