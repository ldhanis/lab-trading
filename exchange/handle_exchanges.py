from datetime import datetime
from locale import currency
from exchange.models import Currency, Pair, ExchangeApi
from account.models import *
from django.utils import timezone
from django.db.models import Q
from trading_platform.views import FIAT_CURRENCY_SYMBOL, calc_evolve

from lab_trading.settings import DEBUG

DAILY_DRAWDOWN = 5
TOTAL_DRAWDOWN = 10

def handle_price_update(pair_symbol, exchange, close_price):
    # Finding pair from pair symbol

    pair_names = pair_symbol.split('/')

    currency_1 = Currency.objects.filter(
        exchange=exchange).get(name=pair_names[0])
    currency_2 = Currency.objects.filter(
        exchange=exchange).get(name=pair_names[1])

    pair = Pair.objects.filter(
        currency_1=currency_1).get(currency_2=currency_2)

    pair.update_value(close_price)
    pair.save()

    orders = None

    update_time = timezone.now()

    DEBUG_PAIR_NAMES = ["ETH/USD"]

    # Retrieve unclosed positions that hasn't been cancelled
    orders = Order.objects.filter(pair=pair).filter(
        position_closed_at=None).filter(order_cancelled_at=None)

    if pair_symbol in DEBUG_PAIR_NAMES:
        print (f'\n \n TOTAL ORDERS FOR {pair_symbol} : {len(orders)}')

    if pair.previous_value < pair.value:
        # Prices went up, that means that we need to open the positions of short orders between old value and new value
        opened_positions = orders.filter(position_opened_at=None).filter(
            entry_price__gte=pair.previous_value).filter(entry_price__lte=pair.value).update(position_opened_at=update_time)

        # We have to close the positions of open Long that have reached their take_profits
        open_long_positions = orders.filter(order_type__iexact='LONG').exclude(position_opened_at=None).filter(take_profit__lte=pair.value)
        open_long_positions.update(take_profit_reached=True)
        open_long_positions = open_long_positions.update(position_closed_at=update_time)


        # We have to close the positions of open Short that have reached their stop_loss
        open_short_positions = orders.filter(order_type__iexact='SHORT').exclude(position_opened_at=None).filter(stop_loss__lte=pair.value)
        open_short_positions.update(stop_loss_reached=True)
        open_short_positions = open_short_positions.update(position_closed_at=update_time)


        if pair_symbol in DEBUG_PAIR_NAMES:
            print(
                f'PRICES INCREASE FOR {pair.krkn_name} {pair.previous_value} -> {pair.value}\n > {opened_positions} POSITIONS opened (Limit) \n > {open_long_positions} LONG closed (TAKE PROFIT) \n > {open_short_positions} SHORT closed (STOP LOSS)')

    elif pair.previous_value > pair.value:
        # Prices went down, that means we have to open the positions of long orders between old value and new value
        opened_positions = orders.filter(position_opened_at=None).filter(
            entry_price__gte=pair.value).filter(entry_price__lte=pair.previous_value).update(position_opened_at=update_time)

        # We have to close the positions of open Short that have reached their take profits
        open_short_positions = orders.filter(order_type__iexact='SHORT').exclude(position_opened_at=None).filter(take_profit__gte=pair.value)
        open_short_positions.update(take_profit_reached=True)
        open_short_positions = open_short_positions.update(position_closed_at=update_time)


        # We have to close the opsitions of open Long that have reached their stop loss
        open_long_positions = orders.filter(order_type__iexact='LONG').exclude(position_opened_at=None).filter(stop_loss__gte=pair.value)
        open_long_positions.update(stop_loss_reached=True)
        open_long_positions = open_long_positions.update(position_closed_at=update_time)


        if pair_symbol in DEBUG_PAIR_NAMES:
            print(
                f'PRICES DECREASE FOR {pair.krkn_name} {pair.previous_value} -> {pair.value}\n > {opened_positions} POSITIONS opened (Limit) \n > {open_long_positions} LONG closed (STOP LOSS) \n > {open_short_positions} SHORT closed (TAKE PROFIT)')

    # handling position openings
    opened_positions = Order.objects.filter(pair=pair).filter(position_opened_at=update_time)

    for position in opened_positions:
        # Get currencies amounts and remove FIAT
        currency_amount_2 = CurrencyAmount.objects.filter(currency=currency_2).filter(trading_screen=position.trading_screen).last()
        currency_amount_2.id = None
        currency_amount_2.amount = currency_amount_2.amount - position.volume
        currency_amount_2.created_on = update_time
        currency_amount_2.save()

        # Add amount of crypto bought if we have a long positionment
        if position.order_type.lower() == 'long':
            currency_amount_1 = CurrencyAmount.objects.filter(currency=currency_1).filter(trading_screen=position.trading_screen).last()
            currency_amount_1.id = None
            currency_amount_1.amount = currency_amount_1.amount + position.volume / position.entry_price
            currency_amount_1.created_on = update_time
            currency_amount_1.save()

        position.handle_opening()

    # handling position closings
    closed_positions = Order.objects.filter(pair=pair).filter(position_closed_at=update_time)
    for position in closed_positions:
        # Increase or decrease currency_amount_1 with profit / loss
        # Calculating profit or loss
        
        currency_amount_1 = CurrencyAmount.objects.filter(currency=currency_1).filter(trading_screen=position.trading_screen).last()
        currency_amount_2 = CurrencyAmount.objects.filter(currency=currency_2).filter(trading_screen=position.trading_screen).last()

        if position.order_type.lower() == 'long':
            # Removing crypto
            currency_amount_1.amount = currency_amount_1.amount - position.volume / position.entry_price
        
        # Adding FIAT
        currency_amount_2.amount = currency_amount_2.amount + position.volume + position.profit_loss

        currency_amount_1.id = None
        currency_amount_1.created_on = update_time
        currency_amount_1.save()

        currency_amount_2.id = None
        currency_amount_2.created_on = update_time
        currency_amount_2.save()

    # Get TradingScreens with open orders on that pair or order that just closed
    trading_screen_ids = Order.objects.filter(pair=pair).filter(Q(position_closed_at=update_time) | Q(position_closed_at=None)).values_list('trading_screen', flat=True)
    trading_screen_ids = [*set(trading_screen_ids)]
    trading_screens = TradingScreen.objects.filter(id__in=trading_screen_ids).filter(enabled=True)

    # For each trading_screen loop to check if has hit drawdown
    date_to = datetime.now() + timedelta(minutes=1)
    date_from = date_to - timedelta(days=1)
    fiat_currency = Currency.objects.filter(
        symbol=FIAT_CURRENCY_SYMBOL).first()

    if len(trading_screens):
        print ('\n CLEANING BAD ACCOUNTS \n')

    for trading_screen in trading_screens:
        used_currencies = Currency.objects.filter(
        currencyamount__trading_screen=trading_screen)

        # Calculating all time first amount evolve
        first_value_all_time, last_value_all_time = trading_screen.get_portfolio_evolution(
            used_currencies, fiat_currency, datetime.min, date_to)
        all_time_evolve = calc_evolve(first_value_all_time, last_value_all_time)

        # Calculating 24h time amount evolve
        first_value_daily, last_value_daily = trading_screen.get_portfolio_evolution(
            used_currencies, fiat_currency, date_from, date_to)
        daily_evolve = calc_evolve(first_value_daily, last_value_daily)

    

        if all_time_evolve < -TOTAL_DRAWDOWN or daily_evolve < -DAILY_DRAWDOWN:
            print ('STOP THIS TRADING SCREEN', trading_screen,all_time_evolve, daily_evolve )
            trading_screen.enabled=False
            trading_screen.save()
            trading_screen.cancel_all_orders()
        else:
            print ('ALL GOOD', trading_screen,all_time_evolve, daily_evolve )