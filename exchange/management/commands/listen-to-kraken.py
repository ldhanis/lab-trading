from django.core.management.base import BaseCommand
import json
import time
import requests
from exchange.models import *
from websocket import create_connection as dj_cc
from exchange.handle_exchanges import *


class Command(BaseCommand):
    help = 'Listens to crypto pairs OHLC in real time on Kraken'

    def handle(self, *args, **kwargs):

        # Creating connection
        ws = dj_cc("wss://ws.kraken.com")

        # List all available assets and update the database
        resp = requests.get('https://api.kraken.com/0/public/Assets')
        resp = resp.json()

        for key, asset_data in resp['result'].items():
            # Checking if asset exists in database
            asset, created = Currency.objects.get_or_create(
                exchange='krkn',
                symbol=key,
                name=asset_data['altname']
            )

            print('created: ' if created else 'got: ', asset)

        available_assets = Currency.objects.filter(exchange='krkn')

        # List all available pairs
        resp = requests.get('https://api.kraken.com/0/public/AssetPairs')
        resp = resp.json()

        all_pairs = []
        for key, value in resp['result'].items():
            ws_name = value['wsname']
            all_pairs.append(ws_name)

            # Checking if pair exists in database
            pair_names = ws_name.split('/')
            currency_1 = available_assets.get(name=pair_names[0])
            currency_2 = available_assets.get(name=pair_names[1])

            pair, created = Pair.objects.get_or_create(
                currency_1=currency_1,
                currency_2=currency_2
            )

            print(pair)

        # Subscribing to all pairs

        ws.send(json.dumps({
            'event': 'subscribe',
            'pair': all_pairs,
            'subscription': {'name': 'ticker'}
        }))

        while True:
            try:
                result = ws.recv()
                result = json.loads(result)

                # Checking if our response if of ticker type

                # print (result, '\n\n')

                if (len(result) == 4):

                    handle_price_update(result[len(result) - 1], 'krkn', result[1]['c'][0])

            except Exception as error:
                print('Caught this error: ' + repr(error))

        ws.close()
