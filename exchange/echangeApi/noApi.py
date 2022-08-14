import * from exchange.models


class NoApi():

    # Returns True everytime

    def authenticate(auth):
        return True

    # Order functions will return

    # Buy or sell according to the market price at the order completion time
    def market_order(pair, direction, volume):
        pass

    # Buy or sell according to a "limit" price
    # If we place a buy order and the market hits the limit price or below, the order is completed
    # If we place a sell order and the market hits the limit price or above, the order is completed
    def limit_order(pair, direction, volume, limit):
        pass

    #
    def stop_loss(pair, volume, trigger_price):
        pass

    # Create a sell order at defined price when the trade is
    def take_profit(pair, volume, trigger_price):
        pass
