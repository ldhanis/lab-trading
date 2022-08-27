from exchange.models import * 
from account.models import *


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
    def market_order(self, user, pair, direction, volume):

        # Create a Buy order

        pass

    # Buy or sell according to a "limit" price
    # If we place a buy order and the market hits the limit price or below, the order is completed
    # If we place a sell order and the market hits the limit price or above, the order is completed
    def limit_order(self, user, pair, direction, volume, limit):
        pass

    #
    def stop_loss(self, user, pair, volume, trigger_price):
        pass

    # Create a sell order at defined price when the trade is
    def take_profit(self, user, pair, volume, trigger_price):
        pass
