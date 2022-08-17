from django.contrib import admin
from account.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(TradingScreen)
admin.site.register(Order)
admin.site.register(CurrencyAmount)