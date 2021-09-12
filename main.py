from binance.client import Client
import pandas as pd
import numpy as np

def moving_avg(df, n):
    MA = pd.Series(df['close'].rolling(n, min_periods=n).mean(), name='MA_' + str(n))
    df = df.join(MA)
    return df

def exponential_moving_avg(df, n):
    EMA = pd.Series(df['close'].ewm(span=n, min_periods=n).mean(), name="EMA_" + str(n))
    df = df.join(EMA)
    return df
'''
def relative_strength_index(df, n):
    i = 0
    UpI = [0]
    DoI = [0]

    while i + 1 <= df.index[-1]:
        UpMove = df.loc[i+1, 'high'] - df.loc[i, 'high']
        DoMove = df.loc[i+1, 'low'] - df.loc[i, 'low']
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1

    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean())
    NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean())
    RSI = pd.Series(PosDI / (PosDI + NegDI), name='RSI_' + str(n))
    df = df.join(RSI)
    return df
'''
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

df = moving_avg(df, 7)
df = moving_avg(df, 25)
df = moving_avg(df, 99)
df = exponential_moving_avg(df, 7)
df = exponential_moving_avg(df, 25)
df = exponential_moving_avg(df, 99)
#df = relative_strength_index(df, 15)
'''
RSI için 6,12,24 periodları olacak!!!
'''
last_row = df.tail(1)

print(last_row['close'])
print(last_row['high'])
print(last_row['MA_7'])
print(last_row['MA_25'])
print(last_row['MA_99'])
print(last_row['EMA_7'])
print(last_row['EMA_25'])
print(last_row['EMA_99'])

'''
Alış için:
 1)   eğer close <= MA_7 ve close >= MA_25 ve close >= MA_99 

 2)   eğer close <= EMA_7 ve close >= EMA_25 ve close >= EMA_99 

 3)   eğer RSI_6 <= 20 veya RSI_12 <= 20

 Satış için:
 1)   eğer close >= MA_7 ve close <= MA_25 ve close <= MA_99 

 2)   eğer close >= EMA_7 ve close <= EMA_25 ve close <= EMA_99 

 3)   eğer RSI_6 >= 80 veya RSI_12 >= 80
'''