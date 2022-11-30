from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from exchange.models import *
from account.models import *
from django.db.models import Max
import copy
import json
from django.contrib import messages
from django.http import JsonResponse

from account.tables import OrderTable, CurrencyTable

FIAT_CURRENCY_SYMBOL = 'ZUSD'

# List assets owned by the user
# Display pairs


def modify_color(code, divider):
    red = str(hex(int(int(f"0x{code[1:3]}", base=16) + (255 -
              int(f"0x{code[1:3]}", base=16)) / divider)))[2:]
    green = str(hex(int(int(f"0x{code[3:5]}", base=16) +
                (255 - int(f"0x{code[3:5]}", base=16)) / divider)))[2:]
    blue = str(hex(int(int(f"0x{code[5:7]}", base=16) +
               (255 - int(f"0x{code[5:7]}", base=16)) / divider)))[2:]

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


def calc_evolve(first_val, last_val):
    if first_val:
        return (last_val - first_val) / first_val * 100
    return last_val


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

    fiat_currency = Currency.objects.filter(
        symbol=FIAT_CURRENCY_SYMBOL).first()

    # getting daily price history of portfolio

    date_to = datetime.now() + timedelta(minutes=1)
    date_from = date_to - timedelta(days=1)
    total_intervals = 24*2

    labels = []
    datasets = []

    # Adding cryptos

    # Finding used_pairs
    used_currencies = Currency.objects.filter(
        currencyamount__trading_screen=trading_screen)
    used_pairs = allowed_pairs.filter(currency_1__in=used_currencies)

    pairs_list = list(allowed_pairs)

    for pair in pairs_list:
        pair.customer_owned_in_dollars = 0

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

        pairs_list_index = pairs_list.index(pair)
        pairs_list[pairs_list_index].customer_owned_in_dollars = pair_portfolio_history[-1]['currency_1_amount_price']

    # Adding fiat (ZUSD)

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

    # Calculating all time first amount evolve
    first_value_all_time, last_value_all_time = trading_screen.get_portfolio_evolution(
        used_currencies, fiat_currency, datetime.min, date_to)
    all_time_evolve = calc_evolve(first_value_all_time, last_value_all_time)

    # Calculating 24h time amount evolve
    first_value_daily, last_value_daily = trading_screen.get_portfolio_evolution(
        used_currencies, fiat_currency, date_from, date_to)
    daily_evolve = calc_evolve(first_value_daily, last_value_daily)

    print('LAST VALUES', last_value_all_time, last_value_daily)

    pairs_list.sort(key=lambda x: x.customer_owned_in_dollars, reverse=True)

    context = {'pairs': pairs_list,
               'daily_portfolio_first_value': first_value_daily,
               'all_time_portfolio_first_value': first_value_all_time,
               'daily_portfolio_evolve': daily_evolve,
               'daily_portfolio_color': calc_evolve_color(daily_evolve),
               'all_time_portfolio_evolve': all_time_evolve,
               'all_time_portfolio_color': calc_evolve_color(all_time_evolve),
               'portfolio_usd_value': last_value_daily,
               'trading_screen': trading_screen,
               'datasets': datasets,
               'labels': labels
               }

    return render(request, 'trader_dashboard.html', context)


def cancel_all_orders(request, trading_screen_id):
    trading_screen = request.user.trading_screens.get(id=trading_screen_id)
    if not trading_screen.enabled:
        messages.warning(
            request, "This trading screen has been blocked due to bad results")
        return redirect('user_dashboard', trading_screen_id=trading_screen_id)

    trading_screen.cancel_all_orders()
    return redirect('user_dashboard', trading_screen_id=trading_screen_id)


def sync_amounts(request, trading_screen_id):
    trading_screen = request.user.trading_screens.get(id=trading_screen_id)
    if not trading_screen.enabled:
        messages.warning(
            request, "This trading screen has been blocked due to bad results")
        return redirect('user_dashboard', trading_screen_id=trading_screen_id)
    trading_screen.sync_currency_amounts()
    return redirect('user_dashboard', trading_screen_id=trading_screen_id)


def trading_dashboard(request, trading_screen_id, currency_1_symbol, currency_2_symbol):

    trading_screen = request.user.trading_screens.get(id=trading_screen_id)
    print(currency_1_symbol, currency_2_symbol)

    if not trading_screen.enabled:
        messages.warning(
            request, "This trading screen has been blocked due to bad results")

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

    orders = Order.objects.filter(trading_screen=trading_screen).filter(
        pair=pair).order_by('-id')

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
        'orders': orders,
    }
    return render(request, 'trading_screen.html', context)

# order_type
# volume
# entry_price
# take_profit
# stop_loss


def create_order(request, trading_screen_id, currency_1_symbol, currency_2_symbol):

    def redirection(error):
        if error:
            messages.warning(request, error)
        return redirect('trading_dashboard', trading_screen_id=trading_screen_id, currency_1_symbol=currency_1_symbol, currency_2_symbol=currency_2_symbol)

    trading_screen = request.user.trading_screens.get(id=trading_screen_id)

    if not trading_screen.enabled:
        return redirection("This trading screen has been blocked due to bad results")

    currency_1 = Currency.objects.get(symbol=currency_1_symbol)
    currency_2 = Currency.objects.get(symbol=currency_2_symbol)
    pair = Pair.objects.filter(currency_1=currency_1).filter(
        currency_2=currency_2).first()

    if request.method == 'POST':
        order_type = request.POST.get('order_type', None)
        volume = float(request.POST.get('volume', None))
        entry_price = float(request.POST.get('entry_price', None))
        take_profit = float(request.POST.get('take_profit', None))
        stop_loss = float(request.POST.get('stop_loss', None))
        leverage = int(request.POST.get('leverage', 2))

        print({
            'trading_screen': trading_screen,
            'currency_1': currency_1,
            'currency_2': currency_2,
            'order_type': order_type,
            'volume': volume,
            'entry_price': entry_price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
        })

        # Checking if ordertype is supported
        if not order_type in ['long', 'short']:

            return redirection(order_type + ' is not supported')

        # Checking if leverage is acceptable
        if order_type == 'short' and leverage < 2:

            return redirection('Leverage does not fit the order type (minimum 2x for short)')

        # Checking if customer has enough balance regarding the collateral balance
        # For further informations, see https://support.kraken.com/hc/en-us/articles/203053116-How-leverage-works-in-spot-transactions-on-margin

        amount_2 = trading_screen.currency_amounts.filter(
            currency=currency_2).last()

        # Checking if enough balance
        if amount_2.amount < volume:

            return redirection('Not enough balance')

        # Checking if entry prices are logical
        current_crypto_market_value = currency_1.get_market_value(
            currency_2_symbol)

        if (order_type == 'long' and entry_price > current_crypto_market_value) or (order_type == 'short' and entry_price < current_crypto_market_value):

            return redirection(f"Entry price ({entry_price}) illogical regarding order type ({order_type}) and current market value ({current_crypto_market_value})")

        # Checking if take_profits is set and if it is logical
        if take_profit and ((order_type == 'long' and entry_price > take_profit) or (order_type == 'short' and entry_price < take_profit)):

            return redirection('Take profits is illogical')

        # Checking if stop_loss is set and if it is logical
        if stop_loss and ((order_type == 'long' and entry_price < stop_loss) or (order_type == 'short' and entry_price > stop_loss)):

            return redirection('Stop loss is illogical')

        # If everything is OK, we create the order

        new_order = Order()

        new_order.order_type = order_type
        new_order.pair = pair
        new_order.leverage = leverage
        new_order.volume = volume
        new_order.entry_price = entry_price
        new_order.take_profit = take_profit
        new_order.stop_loss = stop_loss
        new_order.trading_screen = trading_screen

        new_order.save()

        new_order.handle_creation()
        trading_screen.sync_currency_amounts()

    return redirection(None)


def update_order(request):

    # Debug request

    response = json.loads(request.body)
    order_id = response.get('id')
    entry_price = float(response.get('entryPrice'))
    take_profit = float(response.get('takeProfit'))
    stop_loss = float(response.get('stopLoss'))

    if not (order_id and entry_price and take_profit and stop_loss):
        return JsonResponse({'error': 'missing field'})

    # finding order

    try:
        order = Order.objects.filter(
            trading_screen__user=request.user).get(id=order_id)
    except:
        return JsonResponse({'error': 'order not found'})

    if not order.trading_screen.enabled:
        return JsonResponse({'error':  "This trading screen has been blocked due to bad results"})

    try:
        order.handle_update(entry_price, take_profit, stop_loss)
    except Exception as e:
        return JsonResponse({'error': str(e)})

    return JsonResponse({})


def cancel_order(request, order_id):

    try:
        order = Order.objects.filter(
            trading_screen__user=request.user).get(id=order_id)
    except:
        return JsonResponse({'error': 'order not found'})

    if not order.trading_screen.enabled:
        messages.warning(
            request, "This trading screen has been blocked due to bad results")

    else:

        order.handle_cancel_order()

    return redirect('trading_dashboard', trading_screen_id=order.trading_screen.id, currency_1_symbol=order.pair.currency_1.symbol, currency_2_symbol=order.pair.currency_2.symbol)
