from django import forms

from exchange.models import Exchange, Currency, Pair

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

class CurrencyForm(forms.ModelForm):
	
	name = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Nom'), label_suffix='*:')

	symbol = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Symbole'), label_suffix='*:')

	class Meta:
		model = Currency
		fields = ['name', 'symbol']

class PairForm(forms.ModelForm):

	class Meta:
		model = Pair
		fields = ['currency_1' , 'currency_2' , 'symbol']
	
	name = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
	}), required=True, label=_('Nom'), label_suffix='*:')