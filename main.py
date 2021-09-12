from binance.client import Client
import pandas as pd

with open("api_keys.txt") as f:
    keys = f.readlines()

api_key = keys[0].replace("\n","")
secret_key = keys[1].replace("\n","")

client = Client(api_key, secret_key)

with open('symbol_list.txt') as f:
    symbol_list = f.readlines()

data = [[]]
for sym in symbol_list:
    sym = sym.replace("\n","")
    tmp = client.get_historical_klines(sym, Client.KLINE_INTERVAL_4HOUR,  "1 day ago UTC")
    for i in range(len(tmp)):
        tmp[i].insert(0,sym)
    
    data = data + tmp
del data[0]

for line in data:
    del line[6:]

df = pd.DataFrame(data,columns = ['symbol','date','open','high','low','close'])
df.set_index('date',inplace=True)
df.index = pd.to_datetime(df.index,unit='ms')

print(df)
