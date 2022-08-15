from django.contrib import admin
from exchange.models import ExchangeApi, Currency, Pair
# Register your models here.

admin.site.register(ExchangeApi)
admin.site.register(Currency)
admin.site.register(Pair)