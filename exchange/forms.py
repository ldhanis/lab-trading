from django import forms
from django.utils.translation import gettext_lazy as _

from django.contrib import messages
from exchange.models import Exchange, Currency, Pair, ExchangeApi

import json

class ExchangeForm(forms.ModelForm):

	name = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Name'), label_suffix='*:')

	class Meta:
		model = Exchange
		fields = ['name']

class ExchangeApiForm(forms.ModelForm):

	exchange 			= forms.ModelChoiceField(required = True, queryset = Exchange.objects.all(), label=_('Exchange'), label_suffix='*:', widget=forms.Select(attrs={'class':'form-control'}))
	authentication	 	= forms.JSONField(widget=forms.Textarea(attrs={
		'class': 'form-control'
	}), required=True, label=_('Authentication (JSON FORMAT)'), label_suffix='*:')
		
	class Meta:
		model = ExchangeApi
		fields = ['exchange', 'authentication']
	

class CurrencyForm(forms.ModelForm):
	
	name = forms.CharField(required = True, widget=forms.TextInput(attrs={
		'class': 'form-control'
	}),  label=_('Name'), label_suffix='*:')
	
	exchange 			= forms.ModelChoiceField(required = True, queryset = Exchange.objects.all(), label=_('Exchange'), label_suffix='*:', widget=forms.Select(attrs={'class':'form-control'}))
	
	symbol = forms.CharField(required = True, widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), label=_('symbol'), label_suffix='*:')

	class Meta:
		model = Currency
		fields = ['name','exchange','symbol']

class PairForm(forms.ModelForm):

	currency_1 			= forms.ModelChoiceField(required = True, queryset = Currency.objects.all(), label=_('First Currency'), label_suffix='*:', widget=forms.Select(attrs={'class':'form-control'}))
	currency_2 			= forms.ModelChoiceField(required = True, queryset = Currency.objects.all(), label=_('Second Currency'), label_suffix='*:', widget=forms.Select(attrs={'class':'form-control'}))
	
	symbol = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Symbol'), label_suffix='*:')

	class Meta:
		model = Pair
		fields = ['currency_1' , 'currency_2' , 'symbol']