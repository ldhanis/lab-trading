from django.contrib import admin
from exchange.models import ExchangeApi, Currency, Pair, PairValue
# Register your models here.

admin.site.register(ExchangeApi)
admin.site.register(Currency)
admin.site.register(Pair)
admin.site.register(PairValue)


# Ne pas stocker le cours en temps réel
# Faire des calls api pour récupérer le cours historique