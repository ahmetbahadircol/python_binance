from binance.client import Client
import pandas as pd
import numpy as np

def coin_list():
    with open('symbol_list.txt') as f:
        symbol_list = f.readlines()
    for i in range(len(symbol_list)):
        symbol_list[i] = symbol_list[i].replace("\n","")
    return symbol_list

def main(symbol_list):
    with open("api_keys.txt") as f:
        keys = f.readlines()

    api_key = keys[0].replace("\n","")
    secret_key = keys[1].replace("\n","")

    client = Client(api_key, secret_key)


    data = [[]]
    for sym in symbol_list:
        tmp = client.get_historical_klines(sym, Client.KLINE_INTERVAL_4HOUR,  "34 day ago UTC")
        for i in range(len(tmp)):
            tmp[i].insert(0,sym)
        
        data = data + tmp
    del data[0]

    for line in data:
        del line[6:]

    data = np.array(data)

    df = pd.DataFrame(data,columns = ['symbol','date','open','high','low','close'])

    df['date'] = pd.to_datetime(df['date'],unit='ms')
    df = df.astype({"open" : float,"high" : float, "low" : float, "close" : float})

    return df