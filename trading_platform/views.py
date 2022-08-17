from django.shortcuts import render, redirect
from exchange.models import *
from account.models import *

# List assets owned by the user
# Display pairs


def user_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('login_page')

    # Calculating currency amount max

    portfolio_usd_value = 0

    for currency_amount in CurrencyAmount.objects.filter(user=request.user):
        portfolio_usd_value += currency_amount.get_value('USD')

    context = {'pairs': Pair.objects.filter(active=True).filter(currency_2__symbol='USD').order_by('-value'),
               'portfolio_usd_value': portfolio_usd_value
               }

    return render(request, 'trader_dashboard.html', context)


def trading_dashboard(request, currency_1_symbol, currency_2_symbol):
    print(currency_1_symbol, currency_2_symbol)

    currency_1 = Currency.objects.get(symbol=currency_1_symbol)
    currency_2 = Currency.objects.get(symbol=currency_2_symbol)

    print (currency_1, currency_2)

    # amounts


    try:
        amount_1 = CurrencyAmount.objects.filter(
        user__in=[request.user]).get(currency=currency_1)
    except:
        amount_1 = CurrencyAmount()
        amount_1.currency = currency_1
        amount_1.save()
        amount_1.user.set([request.user])

        print ('HAD TO CREATE',amount_1 )

    try:
        amount_2 = CurrencyAmount.objects.filter(
        user__in=[request.user]).get(currency=currency_2)
    except:
        amount_2 = CurrencyAmount()
        amount_2.currency = currency_2
        amount_2.save()
        amount_2.user.set([request.user])

        print ('HAD TO CREATE',amount_2 )


    print (amount_1, amount_2)

    context = {
        'pair_symbol': '{}{}'.format(currency_1_symbol, currency_2_symbol),
        'amount_1': amount_1,
        'amount_2': amount_2,}
    return render(request, 'trading_screen.html', context)
