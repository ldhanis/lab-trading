from locale import currency
from django.shortcuts import render, redirect
from exchange.models import *
from account.models import *
from django.db.models import Max

# List assets owned by the user
# Display pairs


def user_dashboard(request, trading_screen_id):

    trading_screen = request.user.trading_screens.get(id=trading_screen_id)

    if not request.user.is_authenticated:
        return redirect('login_page')

    # Calculating currency amount max

    portfolio_usd_value = 0

    for currency_amount in trading_screen.currency_amounts.all():
        portfolio_usd_value += currency_amount.get_value('USD')

    context = {'pairs': trading_screen.allowed_pairs.filter(active=True).filter(currency_2__symbol='USD').order_by('-value'),
               'portfolio_usd_value': portfolio_usd_value,
               'trading_screen': trading_screen
               }

    return render(request, 'trader_dashboard.html', context)


def trading_dashboard(request, trading_screen_id, currency_1_symbol, currency_2_symbol):

    trading_screen = request.user.trading_screens.get(id=trading_screen_id)

    print(currency_1_symbol, currency_2_symbol)

    currency_1 = Currency.objects.get(symbol=currency_1_symbol)
    currency_2 = Currency.objects.get(symbol=currency_2_symbol)

    print(currency_1, currency_2)

    # amounts

    amount_1 = trading_screen.currency_amounts.filter(
        currency=currency_1).last()

    if not amount_1:
        amount_1 = CurrencyAmount()
        amount_1.currency = currency_1
        amount_1.trading_screen = trading_screen
        amount_1.save()
        amount_1.user.set([request.user])

        print('HAD TO CREATE', amount_1)

    amount_2 = trading_screen.currency_amounts.filter(
        currency=currency_2).last()

    if not amount_2:
        amount_2 = CurrencyAmount()
        amount_2.currency = currency_2
        amount_2.trading_screen = trading_screen
        amount_2.save()
        amount_2.user.set([request.user])

        print('HAD TO CREATE', amount_2)

    print(amount_1, amount_2)

    context = {
        'pair_symbol': '{}{}'.format(currency_1_symbol, currency_2_symbol),
        'amount_1': amount_1,
        'amount_2': amount_2,
        'currency_1': currency_1,
        'currency_2': currency_2,
        'trading_screen': trading_screen}
    return render(request, 'trading_screen.html', context)


def create_buy_order(request, trading_screen_id, currency_1_symbol, currency_2_symbol, direction='buy'):

    trading_screen = request.user.trading_screens.get(id=trading_screen_id)
    currency_1 = Currency.objects.get(symbol=currency_1_symbol)
    currency_2 = Currency.objects.get(symbol=currency_2_symbol)

    amount_1 = trading_screen.currency_amounts.filter(
        currency=currency_1).last()
    amount_2 = trading_screen.currency_amounts.filter(
        currency=currency_2).last()

    pair = trading_screen.allowed_pairs.filter(currency_1=currency_1).filter(
        currency_2=currency_2).filter(active=True).last()

    if request.method == "POST" and pair:
        amount = float(request.POST.get('amount'))
        limit = request.POST.get('limit')

        # ignore the limit at the moment
        # Check if enough of currency 2 to buy currency 1

        if amount_2.amount >= amount:
            # Create order
            new_order = Order()
            new_order.type_of_order = direction
            new_order.pair = pair
            new_order.trading_screen = trading_screen
            new_order.amount = amount
            new_order.save()

            # Change amounts
            # Do not forget to add fees

            amount_2.amount = amount_2.amount - amount
            amount_2.save()

            print(currency_2)
            print(currency_1.symbol)

            amount_1.amount = amount_1.amount + 1 / \
                currency_1.get_market_value(currency_2.symbol) * amount
            amount_1.save()

    return redirect('trading_dashboard', trading_screen_id=trading_screen_id, currency_1_symbol=currency_1_symbol, currency_2_symbol=currency_2_symbol)
