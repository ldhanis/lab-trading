from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy  as _
from django.db import models

from exchange.models import *

from account.manager import UserManager

# Create your models here.

class User(AbstractUser):

	"""
	User object
	Represents a person 
	"""

	username = None

	email                   = models.EmailField(_('email address'), unique=True)
	
	
	is_staff 				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)
	is_active 				= models.BooleanField(default=True)
	# Spoken language (FR/NL)
	language_code           = models.CharField(max_length=5, default="fr")

	first_name				= models.CharField(max_length=255)
	last_name				= models.CharField(max_length=255)
	phone_numer 			= models.CharField(max_length=15)
	street					= models.CharField(max_length=255)
	number 					= models.CharField(max_length=255)
	box						= models.CharField(max_length=255)
	city 					= models.CharField(max_length=255)
	zip_code				= models.CharField(max_length=32, default='')
	country_code 			= models.CharField(max_length=32, default='')

	# Overriding of the base django user
	USERNAME_FIELD          = 'email'
	REQUIRED_FIELDS         = []

	objects = UserManager()


	@property
	def serialized(self):
		return {
			'email' : self.email,
			'language_code' : self.language_code
		}

class TradingScreen(models.Model):

	user 					= models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="trading_screens")
	allowed_pairs 			= models.ManyToManyField(Pair)
	exchange_api			= models.ForeignKey(ExchangeApi, on_delete=models.CASCADE)

	#def placeOrder(pair)

# possibleType = ["market", "limit", "stop-loss", "take-profit", "stop-loss-limit" ,"take-profit-limit" , "settle-position"]

class Order(models.Model):

	type_of_order 			= models.CharField(max_length=255) 
	pair					= models.ForeignKey(Pair, on_delete=models.CASCADE)
	trading_screen 			= models.ForeignKey(TradingScreen, on_delete=models.CASCADE)
	created_on 				= models.DateTimeField(auto_now_add=True)

class CurrencyAmount(models.Model):

	currency				= models.ForeignKey(Currency, on_delete=models.CASCADE)
	amount					= models.FloatField(default=0)
	user 					= models.ManyToManyField(User)

	def get_value(self, currency_2_symbol):
		if self.currency.symbol == currency_2_symbol:
			return self.amount
		return self.amount * self.currency.get_market_value(currency_2_symbol)

