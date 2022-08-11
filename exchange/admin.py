from django.contrib import admin
from exchange.models import Exchange, ExchangeApi, Currency, Pair
# Register your models here.

admin.site.register(Exchange)
admin.site.register(ExchangeApi)
admin.site.register(Currency)
admin.site.register(Pair)