from datetime import datetime
from time import sleep
import os

from binance.client import Client
from binance import ThreadedWebsocketManager
import yfinance as yf  # For fetching stock data, you may need to install this library as well

import pandas as pd #for data structure

#get API keys
from scr import bnc_key, bnc_sec

def _get_creds():
    #pass API keys
    return bnc_key, bnc_sec
    
def get_all_historic_data(symbol, interval, filename, key=None, secret=None):

    if key is None or secret is None:
        key, secret = _get_creds()

    client = Client(key, secret)

    # get timestamp of earliest date data is available
    timestamp = client._get_earliest_valid_timestamp(symbol, interval)
    #print(timestamp)

    # In the background, this endpoint will continuously query the API in a loop, collecting 1000 price
    # points at a time, until all data from the start point until today is returned.
    # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    bars = client.get_historical_klines(symbol, interval, timestamp, limit=1000)

    #capture 
    bars_df =  pd.DataFrame(bars)
    dir, file = os.path.split(filename)
    file= 'r'+ file
    new_path = os.path.join(dir, file)
    bars_df.to_csv(new_path)
    del bars_df

    #drop all but OCHL+volume:
    for line in bars:
        del line[6:]

    #create a Pandas DataFrame and export to CSV
    pair_df = pd.DataFrame(bars, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], dtype='float64')
    #set data index column:
    pair_df.index = pd.to_datetime(pair_df['Date'], unit="ms")
    pair_df.set_index('Date')

    # pair_df.index.name = 'Date'

    
    # del pair_df['Date']
    
    #export to csv
    pair_df.to_csv(filename)
    
    return pair_df

def get_historic_data(symbol, timestamp, interval, filename, key=None, secret=None):
    
    if key is None or secret is None:
        key, secret = _get_creds()

    client = Client(key, secret)

    # In the background, this endpoint will continuously query the API in a loop, collecting 1000 price
    # points at a time, until all data from the start point until today is returned.
    bars = client.get_historical_klines(symbol, interval, timestamp, limit=1000)

    bars_df =  pd.DataFrame(bars)
    dir, file = os.path.split(filename)
    file= 'r'+ file
    new_path = os.path.join(dir, file)
    bars_df.to_csv(new_path)
    del bars_df

    for line in bars:
        del line[6:]

    #create a Pandas DataFrame and export to CSV
    pair_df = pd.DataFrame(bars, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], dtype='float64')

    pair_df.index = pd.to_datetime(pair_df['Date'], unit="ms")
    del pair_df['Date']
    
    #export to csv
    pair_df.to_csv(filename)
    
    return pair_df

def yf_get_stock_data(symbol, start_date, end_date):
        
    # Fetch historical stock data
    # symbol = "AAPL"
    # start_date = "2023-01-01"
    # end_date = "2023-12-01"

    stock_data = yf.download(symbol, start=start_date, end=end_date)


    # Prepare data for mplfinance
    #ohlc = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']]
    #ohlc.index = mpf.dates.date2num(ohlc.index)


    # Prepare data for mplfinance
    ohlc = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']]
    # ohlc.index = date2num(ohlc.index.to_pydatetime())
    return ohlc

def read_data_tail(filename, tail):

    pair_df = pd.read_csv(filename, index_col=0)
    print (pair_df.shape)
    #print (pair_df)

    ttc_df = pd.DataFrame()
    
    #reduce recent window:
    ttc_df = pair_df[-tail:]
    print (ttc_df.shape)

    ttc_df.index = pd.to_datetime(ttc_df.index)
    #print (ttc_df.columns)
    # print (ttc_df.shape)
    
    return ttc_df



