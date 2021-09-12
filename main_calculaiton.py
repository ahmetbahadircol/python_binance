from typing import no_type_check
from binance.client import Client
from binance.helpers import round_step_size
import pandas as pd
import numpy as np
import get_data

def moving_avg(df, n):
    MA = pd.Series(df['close'].rolling(n, min_periods=n).mean(), name='MA_' + str(n))
    df = df.join(MA)
    return df

def exponential_moving_avg(df, n):
    EMA = pd.Series(df['close'].ewm(span=n, min_periods=n).mean(), name="EMA_" + str(n))
    df = df.join(EMA)
    return df

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

def analysis():
    
    symbol_list = get_data.coin_list()
    df = get_data.main(symbol_list)
    to_buy = []
    to_sell = []
    for coin in symbol_list:
        tmp_df = df[df["symbol"] == coin]
        tmp_df = tmp_df.reset_index()
        #print(tmp_df)

        tmp_df = moving_avg(tmp_df, 7)
        tmp_df = moving_avg(tmp_df, 25)
        tmp_df = moving_avg(tmp_df, 99)
        tmp_df = exponential_moving_avg(tmp_df, 7)
        tmp_df = exponential_moving_avg(tmp_df, 25)
        tmp_df = exponential_moving_avg(tmp_df, 99)
        tmp_df = relative_strength_index(tmp_df, 6)
        tmp_df = relative_strength_index(tmp_df, 12)
        tmp_df = relative_strength_index(tmp_df, 24)

        tmp_df = tmp_df.tail(1)
        print(tmp_df)

        close = tmp_df.iloc[0]["close"]

        MA_7 = tmp_df.iloc[0]["MA_7"]
        MA_25 = tmp_df.iloc[0]["MA_25"]
        MA_99 = tmp_df.iloc[0]["MA_99"]
        EMA_7 = tmp_df.iloc[0]["EMA_7"]
        EMA_25 = tmp_df.iloc[0]["EMA_25"]
        EMA_99 = tmp_df.iloc[0]["EMA_99"]
        RSI_6 = tmp_df.iloc[0]["RSI_6"]
        RSI_12 = tmp_df.iloc[0]["RSI_12"]
        RSI_24 = tmp_df.iloc[0]["RSI_24"]

        if ((close <= MA_7) & (close >= MA_25) & (close >= MA_99) & (close <= EMA_7) & (close >= EMA_25) & (close >= EMA_99) & ((RSI_6 <= 0.2) | (RSI_12 <= 0.2))):
            to_buy.append(coin)
        if ((close >= MA_7) & (close <= MA_25) & (close <= MA_99) & (close >= EMA_7) & (close <= EMA_25) & (close <= EMA_99) & ((RSI_6 >= 0.8) | (RSI_12 >= 0.8))):
            to_sell.append(coin)

    print('Alınacaklar: ')
    print(to_buy)
    print('Satılacaklar: ')
    print(to_sell)

analysis() 

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