from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy  as _

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
