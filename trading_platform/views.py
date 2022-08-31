from locale import currency
from django.shortcuts import render, redirect
from exchange.models import *
from account.models import *
from django.db.models import Max


from account.tables import OrderTable,CurrencyTable

# List assets owned by the user
# Display pairs


def user_dashboard(request, trading_screen_id):

    trading_screen = request.user.trading_screens.get(id=trading_screen_id)

    if not request.user.is_authenticated:
        return redirect('login_page')

    # Calculating currency amount max

    portfolio_usd_value = 0

    for currency_amount in trading_screen.currency_amounts.all():
        portfolio_usd_value += currency_amount.get_value('ZUSD')

    context = {'pairs': trading_screen.allowed_pairs.filter(active=True).filter(currency_2__symbol='ZUSD').order_by('-value'),
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

    
    order_table = OrderTable(Order.objects.filter(trading_screen = trading_screen))
    order_table.paginate(page=request.GET.get("page", 1), per_page=10)

    context = {
        'pair_symbol': '{}{}'.format(currency_1.name, currency_2.name),
        'amount_1': amount_1,
        'amount_2': amount_2,
        'currency_1': currency_1,
        'currency_2': currency_2,
        'trading_screen': trading_screen,
        'order_table' : order_table,
    }
    return render(request, 'trading_screen.html', context)


def create_standard_order(request, trading_screen_id, currency_1_symbol, currency_2_symbol, direction='buy'):

    trading_screen = request.user.trading_screens.get(id=trading_screen_id)
    currency_1 = Currency.objects.get(symbol=currency_1_symbol)
    currency_2 = Currency.objects.get(symbol=currency_2_symbol)

    currency_1_value = trading_screen.currency_amounts.filter(
        currency=currency_1).last()
    currency_2_value = trading_screen.currency_amounts.filter(
        currency=currency_2).last()


    if request.method == 'POST':
        amount = float(request.POST.get('amount')) if len(request.POST.get('amount')) > 0 else 0
        limit = float(request.POST.get('limit')) if len(request.POST.get('limit')) > 0 else 0

        trading_screen.create_order('market' if not limit else 'limit', direction, currency_1_value, currency_2_value, amount,limit)

    return redirect('trading_dashboard', trading_screen_id=trading_screen_id, currency_1_symbol=currency_1_symbol, currency_2_symbol=currency_2_symbol)
