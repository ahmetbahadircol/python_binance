from time import process_time
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

def moving_average_convergence_divergence(df,n1,n2):
    exp1 = df['close'].ewm(span=n1, adjust=False).mean()
    exp2 = df['close'].ewm(span=n2, adjust=False).mean()
    macd = pd.Series((exp1 - exp2), name = 'MACD_' + str(n1) + '_' + str(n2))
    df = df.join(macd)
    return df
    

def MACD_signal(macd,n3):
    exp3 = pd.Series((macd['close'].ewm(span=n3, adjust=False).mean()), name = 'MACD_signal_' + str(n3))
    df = macd.join(exp3)
    return df

def fibo(df,l):
    for coin in l:
        selected = df[df['symbol'] == coin]
        close = selected.tail(1).iloc[0]['close']
        fibb_list = {}
        max_c = selected['close'].max()
        min_c = selected['close'].min()
        print(coin + '[Close: ' + str(close) + '] - [Fibo: ' 
             + str((max_c - min_c) * 0) 
             + ' , ' + str(round(((max_c - min_c) * 0.236),5)) 
             + ' , ' + str(round(((max_c - min_c) * 0.382),5)) 
             + ' , ' + str(round(((max_c - min_c) * 0.500),5)) 
             + ' , ' + str(round(((max_c - min_c) * 0.618),5))
             + ' , ' + str(round(((max_c - min_c) * 0.786),5))
             + ' , ' + str(round(((max_c - min_c) * 1.000),5))
             + ']'
            )
def analysis():
    
    symbol_list = get_data.coin_list()
    df = get_data.main(symbol_list)
    RSI_to_buy = {}
    RSI_to_sell = {}
    m_to_buy = []
    m_to_sell = []
    for coin in symbol_list:
        tmp_df = df[df["symbol"] == coin]
        tmp_df = tmp_df.reset_index()
        #print(tmp_df)

        tmp_df = moving_avg(tmp_df, 7)
        tmp_df = moving_avg(tmp_df, 25)
        tmp_df = moving_avg(tmp_df, 99)
        tmp_df = exponential_moving_avg(tmp_df, 7)
        tmp_df = exponential_moving_avg(tmp_df, 25)
        tmp_df = exponential_moving_avg(tmp_df, 100)
        tmp_df = relative_strength_index(tmp_df, 6)
        tmp_df = relative_strength_index(tmp_df, 12)
        #tmp_df = relative_strength_index(tmp_df, 24)
        tmp_df = moving_average_convergence_divergence(tmp_df,12,26)
        tmp_df = MACD_signal(tmp_df,9)

        tmp_df_last = tmp_df.tail(1)
        #print(tmp_df_last)

        close = tmp_df_last.iloc[0]["close"]

        MA_7 = tmp_df_last.iloc[0]["MA_7"]
        MA_25 = tmp_df_last.iloc[0]["MA_25"]
        MA_99 = tmp_df_last.iloc[0]["MA_99"]
        EMA_7 = tmp_df_last.iloc[0]["EMA_7"]
        EMA_25 = tmp_df_last.iloc[0]["EMA_25"]
        EMA_100 = tmp_df_last.iloc[0]["EMA_100"]
        RSI_6 = tmp_df_last.iloc[0]["RSI_6"]
        RSI_12 = tmp_df_last.iloc[0]["RSI_12"]#14
        #RSI_24 = tmp_df_last.iloc[0]["RSI_24"]
        MACD_12_26 = tmp_df_last.iloc[0]["MACD_12_26"]
        MACDsignal = tmp_df_last.iloc[0]["MACD_signal_9"]

        if ((close <= MA_7) & (close >= MA_25) & (close >= MA_99) & (close <= EMA_7) & (close >= EMA_25) & (close >= EMA_100) & ((RSI_6 <= 0.2) | (RSI_12 <= 0.2))):
            pass
        if ((close >= MA_7) & (close <= MA_25) & (close <= MA_99) & (close >= EMA_7) & (close <= EMA_25) & (close <= EMA_100) & ((RSI_6 >= 0.8) | (RSI_12 >= 0.8))):
            pass

        if (RSI_6 >= 0.65) | (RSI_12 >= 0.65):
            RSIlist = []
            RSIlist.append(RSI_6)
            RSIlist.append(RSI_12)
            RSI_to_buy[coin] = RSIlist

        if (RSI_6 <= 0.35) | (RSI_12 <= 0.35):
            RSIlist = []
            RSIlist.append(RSI_6)
            RSIlist.append(RSI_12)
            RSI_to_sell[coin] = RSIlist
        
        if (close > EMA_100) & (MACD_12_26 > MACDsignal):
            m_to_buy.append(coin)
        
        if (close < EMA_100) & (MACD_12_26 < MACDsignal):
            m_to_sell.append(coin)

    print('MACDye(' + tmp_df.columns[15] + ') göre ALINACAKLAR ve Fibonacci değerleri:\n')
    fibo(df,m_to_buy)
    print('-' * 100)
    print('MACDye(' + tmp_df.columns[15] + ') göre SATILACAKLAR ve Fibonacci değerleri:\n')
    fibo(df,m_to_sell)
    print('-' * 100)
    print('RSIya göre ALINACAKLAR ve RSI değerleri(' + tmp_df.columns[13] + ' ve ' + tmp_df.columns[14] + '):\n')
    for coin in RSI_to_buy:
        print(coin , [round(x,5) for x in RSI_to_buy[coin]])
    print('-' * 100) 
    print('RSIya göre SATILACAKLAR ve RSI değerleri(' + tmp_df.columns[13] + ' ve ' + tmp_df.columns[14] + '):\n')
    for coin in RSI_to_sell:
        print(coin , [round(x,5) for x in RSI_to_sell[coin]])       


analysis() 

