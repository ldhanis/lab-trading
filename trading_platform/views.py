from datetime import datetime, timedelta
from locale import currency
from django.shortcuts import render, redirect
from exchange.models import *
from account.models import *
from django.db.models import Max
import copy

from account.tables import OrderTable, CurrencyTable

FIAT_CURRENCY_SYMBOL = 'ZUSD'

# List assets owned by the user
# Display pairs


def modify_color(code, divider):
    red = str(hex(int(int(f"0x{code[1:3]}", base=16) + (255 -
              int(f"0x{code[1:3]}", base=16)) / divider) ))[2:]
    green = str(hex(int(int(f"0x{code[3:5]}", base=16) +
                (255 - int(f"0x{code[3:5]}", base=16)) / divider) ))[2:]
    blue = str(hex(int(int(f"0x{code[5:7]}", base=16) +
               (255 - int(f"0x{code[5:7]}", base=16)) / divider) ))[2:]

    return f"#{red}{green}{blue}"


def get_color(number):
    colors = [
        '#003f5c',
        '#2f4b7c',
        '#665191',
        '#a05195',
        '#d45087',
        '#f95d6a',
        '#ff7c43',
        '#ffa600',
    ]
    return (colors[number % len(colors)])

def calc_evolve_color(value):
    if (value < 0):
        return '#ff0000'
    return '#00ff00'


def user_dashboard(request, trading_screen_id):

    trading_screen = request.user.trading_screens.get(id=trading_screen_id)

    if not request.user.is_authenticated:
        return redirect('login_page')

    allowed_pairs = trading_screen.allowed_pairs.filter(active=True).filter(
        currency_2__symbol=FIAT_CURRENCY_SYMBOL).order_by('-id')

    # getting daily price history of portfolio

    date_to = datetime.now()
    date_from = date_to - timedelta(days=1)
    total_intervals = 24*2

    labels = []
    datasets = []

    # Adding cryptos

    # Finding used_pairs
    used_currencies = Currency.objects.filter(
        currencyamount__trading_screen=trading_screen)
    used_pairs = allowed_pairs.filter(currency_1__in=used_currencies)

    color_id = 0
    for pair in used_pairs:
        color_code_dark = get_color(color_id)
        color_code_light = modify_color(color_code_dark, 2)
        pair_portfolio_history = trading_screen.get_pair_price_history(
            pair, date_from, date_to, total_intervals)
        dataset = {'label': pair.currency_1.symbol, 'data': [], 'fill': True,
                   'backgroundColor': color_code_light,
                   'pointBackgroundColor': color_code_dark,
                   'borderColor': color_code_dark,
                   'pointHighlightStroke': color_code_dark,
                   'borderCapStyle': 'butt'}

        for i in range(len(pair_portfolio_history)):
            dataset['data'].append(
                pair_portfolio_history[i]['currency_1_amount_price'])

        color_id += 1
        datasets.append(dataset)

    # Adding fiat (ZUSD)

    fiat_currency = Currency.objects.filter(
        symbol=FIAT_CURRENCY_SYMBOL).first()

    currency_portfolio_history = trading_screen.get_currency_amount_history(
        fiat_currency, date_from, date_to, total_intervals)
    color_code_dark = get_color(color_id)
    color_code_light = modify_color(color_code_dark, 2)
    dataset = {'label': fiat_currency.symbol, 'data': [], 'fill': True,
               'backgroundColor': color_code_light,
               'pointBackgroundColor': color_code_dark,
               'borderColor': color_code_dark,
               'pointHighlightStroke': color_code_dark,
               'borderCapStyle': 'butt'}
    for i in range(len(currency_portfolio_history)):
        labels.append(currency_portfolio_history[i]['time'])
        dataset['data'].append(
            currency_portfolio_history[i]['currency_amount'])

    datasets.append(dataset)

    # Calculating start amount and last amount

    start_amount = 0
    last_amount = 0

    for inner_dataset in datasets:
        print('adding', inner_dataset['label'])

        start_amount += inner_dataset['data'][0]
        last_amount += inner_dataset['data'][-1]

    # portfolio evolve
    portfolio_evolve = (last_amount / start_amount * 100) - 100
    

    context = {'pairs': allowed_pairs,
                'portfolio_evolve' : portfolio_evolve,
                'evolve_color' : calc_evolve_color(portfolio_evolve),
               'portfolio_usd_value': last_amount,
               'trading_screen': trading_screen,
               'datasets': datasets,
               'labels': labels
               }

    return render(request, 'trader_dashboard.html', context)


def trading_dashboard(request, trading_screen_id, currency_1_symbol, currency_2_symbol):

    trading_screen = request.user.trading_screens.get(id=trading_screen_id)
    print(currency_1_symbol, currency_2_symbol)

    currency_1 = Currency.objects.get(symbol=currency_1_symbol)
    currency_2 = Currency.objects.get(symbol=currency_2_symbol)

    pair = Pair.objects.filter(currency_1=currency_1).filter(
        currency_2=currency_2).first()
    # amounts

    amount_1 = trading_screen.currency_amounts.filter(
        currency=currency_1).last()

    if not amount_1:
        amount_1 = CurrencyAmount()
        amount_1.currency = currency_1
        amount_1.trading_screen = trading_screen
        amount_1.save()

        print('HAD TO CREATE', amount_1)

    amount_2 = trading_screen.currency_amounts.filter(
        currency=currency_2).last()

    if not amount_2:
        amount_2 = CurrencyAmount()
        amount_2.currency = currency_2
        amount_2.trading_screen = trading_screen
        amount_2.save()

        print('HAD TO CREATE', amount_2)

    print(amount_1, amount_2)

    order_table = OrderTable(Order.objects.filter(trading_screen=trading_screen).filter(
        pair=pair))
    order_table.paginate(page=request.GET.get("page", 1), per_page=10)

    # getting daily price history of portfolio
    date_to = datetime.now()
    date_from = date_to - timedelta(days=1)
    total_intervals = 24 * 4  # Getting updates every 15 minutes

    pair_portfolio_history = trading_screen.get_pair_price_history(
        pair, date_from, date_to, total_intervals)

    context = {
        'pair_symbol': '{}{}'.format(currency_1.name, currency_2.name),
        'amount_1': amount_1,
        'amount_2': amount_2,
        'currency_1': currency_1,
        'currency_2': currency_2,
        'trading_screen': trading_screen,
        'order_table': order_table,
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
        amount = float(request.POST.get('amount')) if len(
            request.POST.get('amount')) > 0 else 0
        limit = float(request.POST.get('limit')) if len(
            request.POST.get('limit')) > 0 else 0

        trading_screen.create_order('market' if not limit else 'limit',
                                    direction, currency_1_value, currency_2_value, amount, limit)

    return redirect('trading_dashboard', trading_screen_id=trading_screen_id, currency_1_symbol=currency_1_symbol, currency_2_symbol=currency_2_symbol)
