import requests
from datetime import datetime, timedelta

def get_pair_price_evolution(pair, since=(datetime.now() - timedelta(days=7)), interval_in_minutes=1440):
    print (since)
    since = datetime.timestamp(since)

    resp = requests.get(f'https://api.kraken.com/0/public/OHLC?pair={pair.krkn_name}&since={since}&interval={interval_in_minutes}')
    resp = resp.json()
    response_list = []
    print (resp)
    if not len(resp['error']):
        
        for key, value in resp['result'].items():
            for ohlc in value:
                response_list.append({
                    'time' : datetime.fromtimestamp(ohlc[0]),
                    'close' : float(ohlc[4])
                })
            break
    
    return (response_list)