from django.contrib import admin
from exchange.models import ExchangeApi, Currency, Pair, PairValue
# Register your models here.

admin.site.register(ExchangeApi)
admin.site.register(Currency)
admin.site.register(Pair)
admin.site.register(PairValue)

# Ne pas stocker le cours en temps réel
# Faire des calls api pour récupérer le cours historique
# Process Flow -> 
# keep multiple API https://support.kraken.com/hc/en-us/articles/360001410583-Transferring-cryptocurrencies-between-two-Kraken-accounts-#:~:text=It%20is%20not%20possible%20to,to%20your%20new%20Kraken%20account.
# Ticker 1 S
# http://localhost:8000/trading/2/XBT/USD 
## Display Bitcoin USD value in real time

# Ajouter les frais dans le sandbox
# Analyser process de vérification des comptes sur Kraken
# Tenir à jour process flow simple
