from datetime import datetime
from exchange.models import Currency, Pair, ExchangeApi
from account.models import *
from django.utils import timezone

def handle_price_update(pair_symbol, exchange, close_price):
    # Finding pair from pair symbol

    pair_names = pair_symbol.split('/')

    currency_1 = Currency.objects.filter(exchange=exchange).get(name=pair_names[0])
    currency_2 = Currency.objects.filter(exchange=exchange).get(name=pair_names[1])

    pair = Pair.objects.filter(currency_1=currency_1).get(currency_2=currency_2)

    pair.update_value(close_price)
    pair.save()

    orders = None
    
    # Find all limit price orders that have been created with a LIMIT
    if pair.previous_value < pair.value:
        print (f'PRICES GO UP FOR {pair.krkn_name} {pair.previous_value} -> {pair.value}')
    
        orders = Order.objects.filter(pair=pair).filter(limit__gte=pair.previous_value).filter(limit__lte=pair.value).filter(direction='sell')
        print(orders.update(fullfilled_on=timezone.now()))

    elif pair.previous_value > pair.value:
        print (f'PRICES DECREASE FOR {pair.krkn_name} {pair.previous_value} -> {pair.value}')

        orders = Order.objects.filter(pair=pair).filter(limit__lte=pair.previous_value).filter(limit__gte=pair.value).filter(direction='buy')
        print(orders.update(fullfilled_on=timezone.now()))
    