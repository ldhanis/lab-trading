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

	exchange 			= forms.ModelChoiceField(queryset = Exchange.objects.all(), label=_('Exchange'), label_suffix='*:', widget=forms.Select(attrs={'class':'form-control'}))
	authentication	 	= forms.JSONField(widget=forms.Textarea(attrs={
		'class': 'form-control'
	}), required=True, label=_('Authentication (JSON FORMAT)'), label_suffix='*:')

	# def clean(self):

	# 	cleaned_data 	= super().clean()
		
	# 	jdata 			= cleaned_data.get('authentication')
	# 	try:
	# 		json_data = json.loads(jdata) 
	# 	except:
	# 		self.add_error("authentication","not a Json input, please enter a Json input.")
		
	class Meta:
		model = ExchangeApi
		fields = ['exchange', 'authentication']
	

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