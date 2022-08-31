import urllib.parse
import hashlib
import hmac
import base64
import time
import os
import requests
import json
import datetime

# Global vars
api_url = "https://api.kraken.com"

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

        print ('--------------------------------------------\n',pair,'\n', direction,'\n', volume, '\n--------------------------------------------')

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "ordertype" : "market",
            "type" : direction,
            "volume" : float(f'{volume:.20f}'),
            "pair" : pair.krkn_symbol
        }

        resp = kraken_request('/0/private/AddOrder', rec_data, self.api_key, self.api_sec)
        resp = resp.json()

        print (resp)

        if len(resp['error']) == 0:
            order_obj.success = True
            order_obj.external_id = resp['result']['txid'][0]
            order_obj.fullfilled_on = datetime.datetime.now()
            order_obj.save()

    def limit_order(self, order_obj):

        pair = order_obj.pair
        direction = order_obj.direction
        volume = order_obj.amount

        print ('--------------------------------------------\n',pair,'\n', direction,'\n', volume, '\n--------------------------------------------')

        rec_data = {
            "nonce": str(int(1000*time.time())),
            "ordertype" : "market",
            "type" : direction,
            "volume" : float(f'{volume:.20f}'),
            "pair" : pair.krkn_symbol,
            "price" : order_obj.limit
        }

        resp = kraken_request('/0/private/AddOrder', rec_data, self.api_key, self.api_sec)
        resp = resp.json()

        print (resp)

        if len(resp['error']) == 0:
            order_obj.success = True
            order_obj.external_id = resp['result']['txid'][0]
            order_obj.save()