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

	user 					= models.ManyToManyField(User)
	allowed_pairs 			= models.ManyToManyField(Pair)
	exchange_api			= models.ForeignKey(ExchangeApi, on_delete=models.CASCADE)

	#def placeOrder(pair)

# possibleType = ["market", "limit", "stop-loss", "take-profit", "stop-loss-limit" ,"take-profit-limit" , "settle-position"]

class Order(models.Model):

	type_of_order 			= models.CharField(max_length=255) 
	pair					= models.ForeignKey(Pair, on_delete=models.CASCADE)
	trading_screen 			= models.ForeignKey(TradingScreen, on_delete=models.CASCADE)
	created_on 				= models.DateTimeField(auto_now_add=True)

class CurrencyAmout(models.Model):

	currency				= models.ForeignKey(Currency, on_delete=models.CASCADE)
	amount					= models.FloatField()
	user 					= models.ManyToManyField(User)
