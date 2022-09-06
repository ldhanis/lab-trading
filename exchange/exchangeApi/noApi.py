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