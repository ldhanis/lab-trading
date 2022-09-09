from exchange.models import * 
from account.models import *
import datetime
from django.utils import timezone

class NoAPI():

    auth = False

    # standard constructor
    def __init__(self, auth_data):
        self.auth = True

    # Returns the value of self.auth

    def authenticate(self):
        return self.auth

    # Order functions will return

    # Buy or sell according to the market price at the order completion time
    def market_order(self, order_obj):

        # Update prices
        # Get current currency_1 amount and currency_2 amount
        user_currency_1_amount = order_obj.trading_screen.currency_amounts.filter(currency=order_obj.pair.currency_1).last()
        user_currency_2_amount = order_obj.trading_screen.currency_amounts.filter(currency=order_obj.pair.currency_2).last()

        # If we have a Buy market order, we diminish the currency_2 in profit of the currency_1 and viceversa
        # Let's create new currency_amount objs to keep an history

        new_user_currency_1_amount, new_user_currency_2_amount = order_obj.trading_screen.new_currency_pair_values(order_obj.pair)

        if order_obj.direction == 'buy':
            new_user_currency_1_amount.amount = user_currency_1_amount.amount + order_obj.amount
            new_user_currency_2_amount.amount = user_currency_2_amount.amount - order_obj.pair.value * order_obj.amount
        else:
            new_user_currency_1_amount.amount = user_currency_1_amount.amount - order_obj.amount
            new_user_currency_2_amount.amount = user_currency_2_amount.amount + order_obj.pair.value * order_obj.amount

        new_user_currency_1_amount.save()
        new_user_currency_2_amount.save()

        order_obj.success = True
        order_obj.external_id = 'noApi'
        order_obj.fullfilled_on=timezone.now()
        order_obj.save()

    # Buy or sell according to a "limit" price
    # If we place a buy order and the market hits the limit price or below, the order is completed
    # If we place a sell order and the market hits the limit price or above, the order is completed
    def limit_order(self, order_obj):
        order_obj.success = True
        order_obj.external_id = 'noApi'
        order_obj.save()

    #
    def stop_loss(self, user, pair, volume, trigger_price):
        pass

    # Create a sell order at defined price when the trade is
    def take_profit(self, user, pair, volume, trigger_price):
        pass


    def get_currencies_amounts(self):
        return {}