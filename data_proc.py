
from time import sleep
from datetime import datetime, timedelta
import os

from binance.client import Client
from binance import ThreadedWebsocketManager
import yfinance as yf  # For fetching stock data, you may need to install this library as well

import pandas as pd #for data structure

#get API keys
from scr import bnc_key, bnc_sec

class DataProc:
    """  data collector/processor """
    def __init__(self, path = '.\\.data\\', pair = 'BTCUSDT', interval = '1h', candles = 100):
        self.bnc_key, self.bnc_sec = self._get_creds()
        self.client = Client(self.bnc_key, self.bnc_sec)

        self.path = path

        self.pair = pair
        self.interval = interval
        self.candles= candles

        self.pair_df = None
        self.data_description = None
        self.csv_data_tail = None

    def _get_creds(self):
        #pass API keys
        return bnc_key, bnc_sec
        
    def get_all_historic_data(self, symbol, interval, filename):

        # get timestamp of earliest date data is available
        timestamp = self.client._get_earliest_valid_timestamp(symbol, interval)
        #print(timestamp)

        # In the background, this endpoint will continuously query the API in a loop, collecting 1000 price
        # points at a time, until all data from the start point until today is returned.
        # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        bars = self.client.get_historical_klines(symbol, interval, timestamp, limit=1000)

        #capture TODO move to data proc also see more recent impl. lower
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

    def get_historic_data(self, symbol, timestamp, interval, savefile=True):
        
         # In the background, this endpoint will continuously query the API in a loop, collecting 1000 price
        # points at a time, until all data from the start point until today is returned.
        bars = self.client.get_historical_klines(symbol, interval, timestamp, limit=1000)

        if savefile == True:
            filename, _ = self.make_file_names(symbol, interval)     
            bars_df =  pd.DataFrame(bars)
            #maybe add postprocessing for capturing data here

            dir, file = os.path.split(filename)
            file= 'r__'+ file
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
        if savefile:
            pair_df.to_csv(filename)
        
        return pair_df

    def yf_get_stock_data(self, symbol, start_date, end_date):
            
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

    def read_csv_data_tail(self, filename, tail):

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
        
        self.csv_data_tail = ttc_df
        return ttc_df

    def make_file_names(self, pair, interval, date=None):
        if date == None:
            current_datetime = datetime.today()
            current_date = current_datetime.date()  # Extract date from datetime
            # current_date_0h = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            current_date = date

        path = self.path

        tc= '-'
        file = pair+tc+interval+current_date.strftime('-%Y-%m-%d')+'.csv'
        m_file = 'm'+file
        filename = path+file
        m_filename = path+m_file

        return filename, m_filename


    def get_new_data(self, candles = 100, pair = 'BTCUSDT', interval='1h'):

        self.pair = pair
        self.interval = interval
        self.candles= candles

        current_datetime = datetime.today()
        filename, m_filename = self.make_file_names(pair, interval, current_datetime)

        # getting the timestamp for binance  
        # datetime.fromisoformat('2023-12-06 00:00:00')
        target_start_time= datetime.fromisoformat(self.calculate_data_span(candles, interval))
        t_start= int(datetime.timestamp(target_start_time)*1000)

        #TODO check here if self.pair_df is good enough and what to bring

        pair_df= self.get_historic_data(symbol=pair, timestamp=t_start, interval=interval, savefile = True)
        # pair_df = pair_df[-candles:] #get only the latest candles

        #TODO store data in the object, 
        # minimize external calls, 
        # advance and store consequently raw data 
        
        self.pair_df = pair_df
    
        return pair_df, filename, m_filename

    def calculate_data_span(self, candle_count, period):
    # Map period to timedelta
        period_mapping = {
            '1m': pd.Timedelta(minutes=1),
            '3m': pd.Timedelta(minutes=3),
            '5m': pd.Timedelta(minutes=5),
            '15m': pd.Timedelta(minutes=15),
            '30m': pd.Timedelta(minutes=30),
            '1h': pd.Timedelta(hours=1),
            '2h': pd.Timedelta(hours=2),
            '4h': pd.Timedelta(hours=4),
            '6h': pd.Timedelta(hours=6),
            '8h': pd.Timedelta(hours=8),
            '12h': pd.Timedelta(hours=12),
            '1d': pd.Timedelta(days=1),
            '1w': pd.Timedelta(weeks=1),
            '1M': pd.Timedelta(days=31),  
        }

        # Calculate the total time span covered by the specified number of candles
        time_span = candle_count * period_mapping.get(period, pd.Timedelta(days=1))

        # Calculate the timestamp in the past
        timestamp_in_past = pd.Timestamp.now() - time_span

        date_format = '%Y-%m-%d %H:%M:%S'    
        timestamp_formatted = timestamp_in_past.strftime(date_format)

        return timestamp_formatted


# PERIOD_ENM = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']




