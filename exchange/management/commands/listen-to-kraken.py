from django.core.management.base import BaseCommand
import json
import time
import requests
from websocket import create_connection as dj_cc


class Command(BaseCommand):
    help = 'Listens to crypto pairs OHLC in real time on Kraken'

    def handle(self, *args, **kwargs):

        # Creating connection
        ws = dj_cc("wss://ws.kraken.com")

        # List all pairs
        resp = requests.get('https://api.kraken.com/0/public/AssetPairs')
        resp = resp.json()

        all_pairs = []
        for key, value in resp['result'].items():
            ws_name = value['wsname']
            all_pairs.append(ws_name)

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
                    tickerResponse = {
                        'close_price' : result[1]['c'][0],
                        'pair' : result[len(result) - 1]
                    }
                    print (tickerResponse)

            except Exception as error:
                print('Caught this error: ' + repr(error))

        ws.close()
