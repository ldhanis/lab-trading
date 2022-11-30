import hashlib
import hmac
import base64
import time
import os
import requests
import json
import datetime
from django.utils import timezone

import urllib


# Global vars
api_url = "https://api.kraken.com"


def toFloatFormat(value):
    return float(f'{value:.20f}')

# Authentication signature function


def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

# Creating a request handler


def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req


class KrakenAPI():

    api_key = None
    api_sec = None

    def __init__(self, auth_data):

        if ('kraken_api_key' in auth_data and 'kraken_api_sec' in auth_data):
            self.api_key = auth_data.get('kraken_api_key')
            self.api_sec = auth_data.get('kraken_api_sec')
        elif (not (self.api_key and self.api_sec)):
            raise Exception('No valid API key')

    def get_currencies_amounts(self):

        # Checking account balance to be sure that the api key is still valid
        resp = kraken_request('/0/private/Balance', {
            "nonce": str(int(1000*time.time()))
        }, self.api_key, self.api_sec)

        ret_arr = {}
        resp = resp.json()

        for symbol, balance in resp['result'].items():
            ret_arr[symbol] = float(balance)

        return (ret_arr)

    def market_order(self, order_obj):

        pair = order_obj.pair
        direction = order_obj.direction
        volume = order_obj.amount

        print('--------------------------------------------\n', pair, '\n',
              direction, '\n', volume, '\n--------------------------------------------')

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "ordertype": "market",
            "type": direction,
            "volume": float(f'{volume:.20f}'),
            "pair": pair.krkn_symbol
        }

        resp = kraken_request('/0/private/AddOrder',
                              rec_data, self.api_key, self.api_sec)
        resp = resp.json()

        print(resp)

        if len(resp['error']) == 0:
            order_obj.success = True
            order_obj.external_id = resp['result']['txid'][0]
            order_obj.fullfilled_on = datetime.datetime.now()
            order_obj.save()

    def limit_order(self, order_obj):

        pair = order_obj.pair
        direction = order_obj.direction
        volume = order_obj.amount

        print('--------------------------------------------\n', pair, '\n',
              direction, '\n', volume, '\n--------------------------------------------')

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "ordertype": "market",
            "type": direction,
            "volume": float(f'{volume:.20f}'),
            "pair": pair.krkn_symbol,
            "price": order_obj.limit
        }

        resp = kraken_request('/0/private/AddOrder',
                              rec_data, self.api_key, self.api_sec)
        resp = resp.json()

        print(resp)

        if len(resp['error']) == 0:
            order_obj.success = True
            order_obj.external_id = resp['result']['txid'][0]
            order_obj.save()

    def update_order_price_txid(self, txid, pair, price):

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "txid": txid,
            "pair": pair,
            "price": toFloatFormat(price)
        }

        resp = kraken_request('/0/private/EditOrder',
                              rec_data, self.api_key, self.api_sec)
        resp = resp.json()

        print(rec_data)
        print('UPDATE ORDER')
        print(resp)

        if len(resp['error']) == 0:
            return resp['result']['txid']
        return None

    def handle_update(self, order, entry_price, take_profit, stop_loss):
        txids = json.loads(order.external_data)

        print('BASE TXIDS', order.external_data)

        entry_price_txid = None
        take_profit_txid = None
        stop_loss_txid = None

        if entry_price and 'base_order_txid' in txids:
            entry_price_txid = self.update_order_price_txid(
                txids['base_order_txid'], order.pair.krkn_symbol, entry_price)
            txids['base_order_txid'] = entry_price_txid if entry_price_txid else txids['base_order_txid']
            order.entry_price = entry_price if entry_price_txid else order.entry_price

        if take_profit and not take_profit == order.take_profit and 'take_profit_txid' in txids:
            take_profit_txid = self.update_order_price_txid(
                txids['take_profit_txid'], order.pair.krkn_symbol, take_profit)
            txids['take_profit_txid'] = take_profit_txid if take_profit_txid else txids['take_profit_txid']
            order.take_profit = take_profit if take_profit_txid else order.take_profit

        if stop_loss and not stop_loss == order.stop_loss and 'stop_loss_txid' in txids:
            stop_loss_txid = self.update_order_price_txid(
                txids['stop_loss_txid'], order.pair.krkn_symbol, stop_loss)
            txids['stop_loss_txid'] = stop_loss_txid if stop_loss_txid else txids['stop_loss_txid']
            order.stop_loss = stop_loss if stop_loss_txid else order.stop_loss

        # update order txid
        order.external_data = json.dumps(txids)
        print('NEW TXIDS', order.external_data)
        order.save()

    def handle_order_creation(self, order_obj):
        # Handling order using the API and Order Obj
        # as stated here : https://docs.kraken.com/rest/#tag/User-Trading/operation/addOrder
        # and here : https://support.kraken.com/hc/en-us/articles/360038640052-Conditional-Close
        # we can create a "base order" that will open the position and set the stop-loss
        # we just then have to create a "take profit" as soon as the main order is started
        # See the function below handle_order_opening

        # We need to create a limit order
        ordertype = 'limit'

        # Using the "type" as the direction (sell if short selling, buy if long buying)
        type = 'sell' if order_obj.order_type.lower() == 'short' else 'buy'

        # everything else is linked to the intrinsic values of the order_obj
        # dividing by the entry price to get the amount  wished in the "base asset"
        volume = order_obj.volume / order_obj.entry_price
        pair = order_obj.pair.krkn_symbol
        price = order_obj.entry_price
        leverage = order_obj.leverage

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "ordertype": ordertype,
            "type": type,
            # "close[price]": toFloatFormat(order_obj.stop_loss),
            # "close[ordertype]": 'stop-loss',
            "volume": toFloatFormat(volume),
            "pair": pair,
            "price": toFloatFormat(price),
            "leverage": None if leverage == 0 else leverage,
        }

        resp = kraken_request('/0/private/AddOrder',
                              rec_data, self.api_key, self.api_sec)
        resp = resp.json()

        print('Start order')
        print(rec_data)
        print(resp)

        if len(resp['error']) == 0:
            try:
                old_txid = json.loads(order_obj.external_data)
            except:
                old_txid = {}

            old_txid['base_order_txid'] = resp['result']['txid'][0]
            order_obj.external_data = json.dumps(old_txid)
            order_obj.save()

    def handle_stop_loss(self, order_obj):
        # Crating the stop-loss

        ordertype = 'stop-loss'

        # Invert direction for stop loss
        type = 'buy' if order_obj.order_type.lower() == 'short' else 'sell'
        # dividing by the entry price to get the amount  wished in the "base asset"
        volume = order_obj.volume / order_obj.entry_price
        price = order_obj.stop_loss
        pair = order_obj.pair.krkn_symbol
        leverage = order_obj.leverage

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "ordertype": ordertype,
            "type": type,
            "volume": toFloatFormat(volume),
            "pair": pair,
            "price": toFloatFormat(price),
            "leverage": None if leverage == 0 else leverage,
        }

        if leverage > 0:
            rec_data["reduce_only"] = True

        resp = kraken_request('/0/private/AddOrder',
                              rec_data, self.api_key, self.api_sec)

        resp = resp.json()

        print('STOP LOSS')
        print(rec_data)
        print(resp)

        if len(resp['error']) == 0:
            order_obj.success = True

            try:
                old_txid = json.loads(order_obj.external_data)
            except:
                old_txid = {}

            old_txid['stop_loss_txid'] = resp['result']['txid'][0]

            order_obj.external_data = json.dumps(old_txid)
            order_obj.save()

    def handle_take_profit(self, order_obj):
        # Crating the take-profit

        ordertype = 'take-profit'

        # Invert direction for take profit
        type = 'buy' if order_obj.order_type.lower() == 'short' else 'sell'
        # dividing by the entry price to get the amount  wished in the "base asset"
        volume = order_obj.volume / order_obj.entry_price
        price = order_obj.take_profit
        pair = order_obj.pair.krkn_symbol
        leverage = order_obj.leverage

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "ordertype": ordertype,
            "type": type,
            "volume": toFloatFormat(volume),
            "pair": pair,
            "price": toFloatFormat(price),
            "leverage": None if leverage == 0 else leverage,
        }

        if leverage > 0:
            rec_data["reduce_only"] = True

        resp = kraken_request('/0/private/AddOrder',
                              rec_data, self.api_key, self.api_sec)
        resp = resp.json()

        print('Take profit')
        print(rec_data)
        print(resp)

        if len(resp['error']) == 0:
            order_obj.success = True

            try:
                old_txid = json.loads(order_obj.external_data)
            except:
                old_txid = {}

            old_txid['take_profit_txid'] = resp['result']['txid'][0]

            order_obj.external_data = json.dumps(old_txid)
            order_obj.save()

    def create_liquidation_market_order(self, order_obj):
        ordertype = 'market'

        # Invert direction for take profit
        type = 'buy' if order_obj.order_type.lower() == 'short' else 'sell'
        # dividing by the entry price to get the amount  wished in the "base asset"
        volume = order_obj.volume / order_obj.entry_price
        pair = order_obj.pair.krkn_symbol
        leverage = order_obj.leverage

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "ordertype": ordertype,
            "type": type,
            "volume": toFloatFormat(volume),
            "pair": pair,
            "leverage": None if leverage == 0 else leverage,
        }

        if leverage > 0:
            rec_data["reduce_only"] = True

        resp = kraken_request('/0/private/AddOrder',
                              rec_data, self.api_key, self.api_sec)
        resp = resp.json()

        print('Take profit')
        print(rec_data)
        print(resp)

        if len(resp['error']) == 0:
            order_obj.success = True

            try:
                old_txid = json.loads(order_obj.external_data)
            except:
                old_txid = {}

            old_txid['liquidation_txid'] = resp['result']['txid'][0]

            order_obj.external_data = json.dumps(old_txid)
            order_obj.save()


    def get_open_orders(self):

        rec_data = {
            "nonce": str(int(1000*time.time())),
            'trades': True
        }

        resp = kraken_request('/0/private/OpenOrders',
                              rec_data, self.api_key, self.api_sec)
        return resp.json()

    def cancel_order(self, order_obj):

        # Checking if order has not already been liquidated or if external data has at least been set
        if not order_obj.external_data:
            return
        
        # Getting Txids of orders that we have to cancel
        txids = json.loads(order_obj.external_data)

        if 'liquidation_txid' in txids or order_obj.position_closed_at or order_obj.position_closed_at:
            return

        # Syncing order with kraken
        self.sync_order_infos(order_obj)

        if order_obj.position_opened_at:
            # Creating a market order reverse with the same values as the base order to liquidate position
            self.create_liquidation_market_order(order_obj)



        rec_data = {
            "nonce": str(int(1000*time.time())),
            "orders": []
        }

        if 'base_order_txid' in txids and order_obj.position_opened_at:
            rec_data['orders'].append(txids['base_order_txid'])

        if 'stop_loss_txid' in txids:
            rec_data['orders'].append(txids['stop_loss_txid'])

        if 'take_profit_txid' in txids:
            rec_data['orders'].append(txids['take_profit_txid'])

        # Cancelling all orders

        print (rec_data)

        # rec_data['orders'] = ','.join(rec_data['orders'])

        # print (rec_data)

        resp = kraken_request('/0/private/CancelOrderBatch',
                              rec_data, self.api_key, self.api_sec)

        print (resp.json())

        order_obj.order_cancelled_at = timezone.now()
        order_obj.save()

    def cancel_all_orders(self, orders):

        rec_data = {
            "nonce": str(int(1000*time.time()))
        }

        resp = kraken_request('/0/private/CancelAll',
                              rec_data, self.api_key, self.api_sec)

        print(resp)

        orders = orders.filter(position_opened_at=None).filter(
            position_closed_at=None).filter(order_cancelled_at=None)
        orders.update(order_cancelled_at=timezone.now())

    def sync_order_infos(self, order_obj):

        # Listing txids

        stored_txids = json.loads(order_obj.external_data)

        txids = ','.join(stored_txids.values())

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "txid": txids
        }

        resp = kraken_request('/0/private/QueryOrders',
                              rec_data, self.api_key, self.api_sec)

        jsresp = resp.json()
        if len(jsresp['error']) == 0:
            for order_txid, value in jsresp['result'].items():
                # Checking type of order and updating the results of the order
                if value['status'] == 'closed' and value['descr']['ordertype'] == 'limit':
                    # We have to set the position as opened
                    order_obj.position_opened_at = datetime.datetime.fromtimestamp(value['closetm'])
                
                if value['status'] == 'closed' and value['descr']['ordertype'] == 'stop-loss':
                    # we have the stop loss that has triggered
                    order_obj.position_closed_at = datetime.datetime.fromtimestamp(value['closetm'])
                    order_obj.stop_loss_reached = True
                    order_obj.take_profit_reached = False

                if value['status'] == 'closed' and value['descr']['ordertype'] == 'take-profit':
                    order_obj.position_closed_at = datetime.datetime.fromtimestamp(value['closetm'])
                    order_obj.stop_loss_reached = False
                    order_obj.take_profit_reached = True
            
            order_obj.save()