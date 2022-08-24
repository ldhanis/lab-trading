from exchange.models import Currency, Pair, ExchangeApi

def handle_price_update(pair_symbol, exchange, close_price):
    # Finding pair from pair symbol

    pair_names = pair_symbol.split('/')

    currency_1 = Currency.objects.filter(exchange=exchange).get(symbol=pair_names[0])
    currency_2 = Currency.objects.filter(exchange=exchange).get(symbol=pair_names[1])

    pair = Pair.objects.filter(currency_1=currency_1).get(currency_2=currency_2)

    pair.update_value(close_price)
    pair.save()
    print (pair, close_price)