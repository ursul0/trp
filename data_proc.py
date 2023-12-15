
from time import sleep
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os

from binance.client import Client
from binance import ThreadedWebsocketManager
import yfinance as yf  # For fetching stock data, you may need to install this library as well

import pandas as pd #for data structure

import threading

#get API keys
from scr import bnc_key, bnc_sec

DEBUG_PRINT = 1

# data defaults
SYMBOLS = ['BTCUSDT', 'ETHUSDT']
INTERVALS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
# PAIR_DATA = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])


# print("test")


TOTAL_CANDLES = 100
SYMBOL = 'BTCUSDT'
INTERVAL ='1m'




class DataProc:
    """  data collector/processor """
    def __init__(self, path = '.\\.data\\', pair = SYMBOL, interval = INTERVAL, candles = TOTAL_CANDLES):
        self.bnc_key, self.bnc_sec = self._get_creds()
        self.client = Client(self.bnc_key, self.bnc_sec)

        self.lock = threading.Lock()

        self.path = path
        self.pair = pair

        self.interval = interval
        self.candles= candles
        self.pair_df_last_date = None

        self.pair_df = None
        self.pair_df_store = self.create_data_store()
        self.data_map = self.initialize_data_map()

    def create_data_store(self):
        data_store = {}
        for pairs in SYMBOLS: 
            data_store[pairs] = {}
            for interval in INTERVALS:
                # Initialize 'LastDate' and 'StartDate' to None for the '1m' period
                data_store[pairs][interval] = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'], index=pd.to_datetime([]))
        return data_store
    
    def initialize_data_map(self):
        data_structure = {}

        for pair in SYMBOLS:
            data_structure[pair] = {}
            for interval in INTERVALS:
                data_structure[pair][interval] = {'StartDate': None, 'EndDate': None, 'Updated': None}

        return data_structure


    def populate_intervals_with_data_slice(self, pair, interval, candles):
        # Populate pair_df with data for the specified interval
        for interval in self.pair_df_bInt:
            print(f'getting {interval} interval')
            interval = self.get_new_data(pair=pair, interval=interval, candles=candles)
        else:
            print(f"Invalid interval: {interval}. Please choose from: {', '.join(self.intervals)}")

    def _get_creds(self):
        #pass API keys
        return bnc_key, bnc_sec
 
    def get_historic_data2(self, symbol, timestamp, interval, savefile=True):

        t_old= self.data_map[symbol][interval]['Updated'] 
        t_cur =pd.Timestamp.now() 
        t_span = t_cur- t_old

        t_interval = self.calculate_data_span(1, interval)

        # with self.lock:
        # if self.data_status[symbol].[interval]
        if self.pair_df_store[symbol][interval].empty or t_span>t_interval:  
            # In the background, this endpoint will continuously query the API in a loop, collecting 1000 price
            # points at a time, until all data from the start point until today is returned.
            bars = self.client.get_historical_klines(symbol, interval, timestamp, limit=1000)

            # if savefile == True:
            #     filename, _ = self.make_file_names(symbol, interval)     
            #     bars_df =  pd.DataFrame(bars)
            #     #maybe add postprocessing for capturing data here

            #     dir, file = os.path.split(filename)
            #     dir = dir+'\\.raw\\'
            #     file= 'r__'+ file
            #     new_path = os.path.join(dir, file)
            #     bars_df.to_csv(new_path)
            #     del bars_df

            bars_reduced = [line[:-6] for line in bars]

            #create a Pandas DataFrame ready for mplfinance and pass & export to CSV
            #create a Pandas DataFrame and export to CSV
            pair_df = pd.DataFrame(bars_reduced, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], dtype='float64')

            pair_df.index = pd.to_datetime(pair_df['Date'], unit="ms")
            del pair_df['Date']
            # pair_df.index.name = 'Date'
    
            self.pair_df_store[symbol][interval] = pair_df
            # first_candle_values = self.pair_df_store[symbol][interval].iloc[0]
            
            self.pair_df = self.pair_df_store[symbol][interval]
            self.data_map[symbol][interval]['StartDate'] = self.pair_df_store[symbol][interval].index[0]
            self.data_map[symbol][interval]['EndDate'] = self.pair_df_store[symbol][interval].index[-1]
            self.data_map[symbol][interval]['Updated'] = pd.Timestamp.now()
        
        # elif self.pair_df_store[symbol][interval]
        #     last_date2 = self.pair_df_store[interval]['LastDate'].iloc[0]
            


        else:
            last_date = self.pair_df_store[symbol][interval].index[-1]
            if DEBUG_PRINT == 1:
                print(f'We have got local cache hit on {last_date}')
            self.pair_df = self.pair_df_store[symbol][interval]

        # if savefile == True:
        #     self.pair_df.to_csv(savefile)
                    
        return self.pair_df
    

    def get_historic_data(self, symbol, timestamp, interval):

        t_start= int(datetime.timestamp(timestamp)*1000)

        bars = self.client.get_historical_klines(symbol, interval, t_start, limit=1000)
        bars_reduced = [line[:-6] for line in bars]

        pair_df = pd.DataFrame(bars_reduced, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], dtype='float64')
        pair_df.index = pd.to_datetime(pair_df['Date'], unit="ms")
        del pair_df['Date']
        pair_df.index.name = 'Date'
                        
        return pair_df


    def get_new_data(self, candles = TOTAL_CANDLES, pair = SYMBOL, interval=INTERVAL, savefile = True):
        
         #TODO: review below and reduce the crap
        current_datetime = datetime.today()
        filename, m_filename = self.make_file_names(pair, interval, current_datetime)

        # target_start_time= datetime.fromisoformat(self.calculate_data_span(candles, interval))
        # t_start= int(datetime.timestamp(target_start_time)*1000)

        cur_time = pd.Timestamp.now()
        upd_time = self.data_map[pair][interval]['Updated']
        candle_t,_ = self.calculate_data_span(1, interval)
        candle_t=candle_t-pd.Timestamp.now()
     
        if upd_time == None: #fresh data needed
            target_start_time,_ = self.calculate_data_span(candles, interval)
            pair_df = self.get_historic_data(symbol=pair, timestamp=target_start_time, interval=interval)
            
            if savefile == True:
                pair_df.to_csv(filename)
            
            self.pair_df_store[pair][interval] = pair_df
            self.data_map[pair][interval]['StartDate'] = self.pair_df_store[pair][interval].index[0]
            self.data_map[pair][interval]['EndDate'] = self.pair_df_store[pair][interval].index[-1]
            self.data_map[pair][interval]['Updated'] = pd.Timestamp.now()

        elif  upd_time - cur_time > candle_t:
            candles_to_get = round((upd_time - cur_time)/candle_t)
            target_start_time,_ = self.calculate_data_span(candles_to_get, interval)
            #update 10 last candles
            pair_df = self.get_historic_data(symbol=pair, timestamp=target_start_time, interval=interval)
  
            self.data_map[pair][interval]['EndDate'] = self.pair_df_store[pair][interval].index[-1]
            self.data_map[pair][interval]['Updated'] = pd.Timestamp.now()

            df = self.pair_df_store[pair][interval]
            # Append existing data with the new and assign it back to df
            # df = pd.concat([df, pair_df], ignore_index=True)
            df = pd.concat([df, pair_df])
            self.pair_df_store[pair][interval] = df

    
            
  
    
        else:
            last_date = self.pair_df_store[pair][interval].index[-1]
            if DEBUG_PRINT == 1:
                print(f'We have got local cache hit on {last_date}')
     
        #return only th erequested number of candles
        return self.pair_df_store[pair][interval].iloc[-candles:], filename, m_filename




    def get_all_historic_data(self, symbol, interval, filename):

        ##SHOIULD NOT BE WORKING AS IT IS
         last_date = self.pair_df_store[interval]['LastDate']

         if last_date == None: #data NOT available locally 

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

            #TODO get dataframe from appropriate period in self.pair_df_bInt, 
                # initialize proper inetval that contains dta from the arrived object - bars
                # store 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', store as is, also set 'Interval' feature with 1 (for current period for future cross reference )
                

            self.pair_df = pd.DataFrame(bars, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], dtype='float64')
            #set data index column:
            self.pair_df.index = pd.to_datetime(self.pair_df['Date'], unit="ms")
            self.pair_df.index.name = 'Date'
            self.pair_df.set_index('Date')
            del self.pair_df['Date']
        
         elif last_date != None:
            if DEBUG_PRINT == 1:
                print('We have got local cache hit on {last_date}')
                self.pair_df = self.pair_df_store[interval]
                self.pair_df_last_date = last_date
            
        #export to csv
        # df.to_csv(filename)
         
         return self.pair_df


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

        self.dataframes_tuple = self.create_dataframes_tuple()

    def check_and_get_last_date(self):
        
        for interval, df in self.pair_df_bInt.items():
            if not df.empty:  # Check if the DataFrame is not empty
                t_date = df.iloc[-1]['Date']  # Get 'Date' from the last row

                if DEBUG_PRINT == 1:
                    print(f'We have got local cache hit for interval {interval}! {t_date}')

                return t_date, interval, df  # Return the 'Date' value if found

        return None 


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

        return timestamp_in_past, timestamp_formatted





