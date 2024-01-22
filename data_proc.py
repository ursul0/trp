
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

DEBUG_PRINT = 0
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT']
# data defaults

INTERVALS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
# PAIR_DATA = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

#this is not the way:
INTERVALS_ON_APPEND = 1

TOTAL_CANDLES = 100

DEF_SYMBOL = 'BTCUSDT'
DEF_INTERVAL ='4h'

DATA_REFRESH_RATE = 1 #data refresh in candles (one means we poll the candle historical data)

class DataProc:
    """ 
        data collector/processor
        gets historic oclh+volume from binanca, stores in pair_df_store[SYMBOLS][INTERVALS]
        uses TOTAL_CANDLES as "fixed screen size"

    """
    def __init__(self, path = '.\\.data\\', pair = DEF_SYMBOL, interval = DEF_INTERVAL, candles = TOTAL_CANDLES):
        self.bnc_key, self.bnc_sec = self._get_creds()
        self.client = Client(self.bnc_key, self.bnc_sec)

        # self.lock = threading.Lock()
        # f'{path}\\{pair}\\{interval}'
        self.path = path

        self.pair = pair
        self.interval = interval
        self.candles= candles
        
        #files
        self.savedata = True
        self.file, self.m_file = self._make_file_names_new()
       
        #data structures
        # self.pair_df = None
        self.pair_df_store = self._create_data_store()
        self.data_map = self._initialize_data_map()


        self.pair_df = self.get_data(self.pair, self.interval)


    def _get_creds(self):
        #pass API keys
        return bnc_key, bnc_sec
 
    # def set_data_details(self, pair, interval, candles):
    #     self.pair = pair
    #     self.interval = interval
    #     self.candles= candles
    #     current_datetime = datetime.today()
    #     self.file, self.m_file = self._make_file_names(self, pair, current_datetime)
    #     return self.file, self.m_file
    
    def _create_data_store(self):
        data_store = {}
        for pairs in SYMBOLS: 
            data_store[pairs] = {}
            for interval in INTERVALS:
                # Initialize 'LastDate' and 'StartDate' to None for the '1m' period
                data_store[pairs][interval] = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'], index=pd.to_datetime([]))
        return data_store
    
    def _initialize_data_map(self):
        data_structure = {}

        for pair in SYMBOLS:
            data_structure[pair] = {}
            for interval in INTERVALS:
                data_structure[pair][interval] = {'StartDate': None, 'EndDate': None, 'Updated': None}

        return data_structure

    def _save_data_store(self):
        pd.DataFrame(self.pair_df_store).to_csv((self.file+'.datastore'))

    def _get_historic_data_BNNC(self, symbol, timestamp, interval):

        t_start= int(datetime.timestamp(timestamp)*1000)

        bars = self.client.get_historical_klines(symbol, interval, t_start, limit=1000)
        bars_reduced = [line[:-6] for line in bars]

        pair_df = pd.DataFrame(bars_reduced, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], dtype='float64')
        pair_df.index = pd.to_datetime(pair_df['Date'], unit="ms")
        del pair_df['Date']
        # pair_df.index.name = 'Date'
                        
        return pair_df

    def get_data(self,  pair = DEF_SYMBOL, interval=DEF_INTERVAL, refresh = False, savedata = True):
        
        self.pair = pair 
        self.interval = interval 
        upd_time = self.data_map[pair][interval]['Updated']
        #screen size of data
        #check for .empty() 
        if upd_time == None or refresh == True: #fresh data is needed 

            target_start_time,_ = self._calculate_data_span(TOTAL_CANDLES, interval)
            pair_df = self._get_historic_data_BNNC(symbol=pair, timestamp=target_start_time, interval=interval)
            cur_time = pd.Timestamp.now()
            #TODO consiger removing file operation from here!
            # if savedata == True:
            #     pair_df.to_csv(self.file)
            
            self.pair_df_store[pair][interval] = pair_df
            self.data_map[pair][interval]['StartDate'] = self.pair_df_store[pair][interval].index[0]
            self.data_map[pair][interval]['EndDate'] = self.pair_df_store[pair][interval].index[-1]
            
            upd_time = cur_time
            self.data_map[pair][interval]['Updated'] = upd_time
            #if 1 is needed - processed sepparately
            # self.pair_df = pair_df.copy(deep=True)
            self.pair_df = pair_df
            self.pair = pair
            self.interval = interval
        
        return self.pair_df_store[pair][interval].iloc[-TOTAL_CANDLES:], self.pair, self.interval 
        

    def _self_append_data(self,  pair = DEF_SYMBOL, interval=DEF_INTERVAL):
        #NOT WORKING, JUST A COPY OF SOMETHING RELEVANT 
        #  a new one self.get_upd_data()


        if pair == DEF_SYMBOL:
            pair = self.pair
        if interval == DEF_INTERVAL:
            interval = self.interval

        # candles = TOTAL_CANDLES
        cur_time = pd.Timestamp.now()
        upd_time = self.data_map[pair][interval]['Updated']
        
        candle_t,_ = self._calculate_data_span(1, interval)
        candle_t=candle_t-pd.Timestamp.now()

        #checking if candle time has passed, to get a new one
        if (upd_time - cur_time).total_seconds()/candle_t.total_seconds() > 1:
            target_start_time,_ = self._calculate_data_span(1, interval)
            tgt_timestamp = pd.Timestamp(target_start_time)
            # tgt_timestamp = pd.to_timedelta(target_start_time)
            #update x last candles

            pair_df = self.get_historic_data(symbol=pair, timestamp=tgt_timestamp, interval=interval)

            # self.pair_df_store[pair][interval] = pair_df
            self.data_map[pair][interval]['EndDate'] = self.pair_df_store[pair][interval].index[-1]
            self.data_map[pair][interval]['Updated'] = pd.Timestamp.now()

            # pair_df.at[index_to_replace, 'Value'] = new_value

            self.pair_df_store[pair][interval] = pd.concat([self.pair_df_store[pair][interval], pair_df])
            #maybe cleanup df.drop_duplicates()
        #  self.pair_df, self.pair, self.interval = self.data_proc._append_data() 
        return self.pair_df_store[pair][interval].iloc[-TOTAL_CANDLES:], pair, interval        

    def get_upd_data(self,  pair = DEF_SYMBOL, interval=DEF_INTERVAL):
        #temp solution
        #TODO implement proper append mechanism
        # if pair == DEF_SYMBOL:
        pair = self.pair 
        # if interval == DEF_INTERVAL:
        interval = self.interval

        # candles = TOTAL_CANDLES
        cur_time = pd.Timestamp.now()
        upd_time = self.data_map[pair][interval]['Updated']
        candle_t,_ = self._calculate_data_span(1, interval)
        candle_t=candle_t-pd.Timestamp.now()

        try:
            ex_start_time = self.data_map[pair][interval]['StartDate']
        except KeyError: 
            return self.get_data(self,  pair, interval, True)
        
        # if (upd_time - cur_time).total_seconds()/candle_t.total_seconds() > float(DATA_REFRESH_RATE/90):
        # self.data_map[pair][interval]['StartDate'] = self.pair_df_store[pair][interval].index[0]
    
        target_start_time,_ = self._calculate_data_span(INTERVALS_ON_APPEND, interval)
        tgt_timestamp = pd.Timestamp(target_start_time)
        # tgt_timestamp = pd.to_timedelta(target_start_time)
        #update x last candles

        pair_df = self._get_historic_data_BNNC(symbol=pair, timestamp=tgt_timestamp, interval=interval)
        cur_time = pd.Timestamp.now()
        new_dta_time = pair_df.index[-1]

        # print(f'appending existing data from {(ex_start_time)} up to {new_dta_time} updated at: {cur_time}')

        # actually append, not replace
        # self.data_map[pair][interval]['StartDate'] = self.pair_df_store[pair][interval].index[0]
        
        #old way, untested
        # self.pair_df_store[pair][interval] = pd.concat([self.pair_df_store[pair][interval], pair_df])

        df = self.pair_df_store[pair][interval]
        df = pd.concat([df, pair_df])
        # Keep last duplicates
        self.pair_df_store[pair][interval] =  df.loc[~df.index.duplicated(keep='last')]


        # self.pair_df_store[pair][interval] = pair_df
        self.data_map[pair][interval]['EndDate'] = self.pair_df_store[pair][interval].index[-1]
        self.data_map[pair][interval]['Updated'] = cur_time

        self.pair_df = df.iloc[-TOTAL_CANDLES:]

        return self.pair_df_store[pair][interval].iloc[-TOTAL_CANDLES:], pair, interval


    def _get_all_historic_data(self, symbol, interval, filename):

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
            del self.pair_df['Date']
            self.pair_df.index.name = 'Date'
        
        elif last_date != None:
            if DEBUG_PRINT == 1:
                print('We have got local cache hit on {last_date}')
                self.pair_df = self.pair_df_store[interval]
                self.pair_df_last_date = last_date
            
        #export to csv
        # df.to_csv(filename)
        return self.pair_df

    def _yf_get_stock_data(self, symbol, start_date, end_date):
            
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

    def _read_csv_data_tail(self, filename, tail):

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

    def _make_file_names(self):
   
        current_datetime = datetime.today()
        current_date = current_datetime.date()  # Extract date from datetime

        #if not provided as parameters, take presets from the class
        # path = path if path is not None else self.path
        # pair = pair if pair is not None else self.pair
        # interval = interval if interval is not None else self.interval

        path = self.path
        pair = self.pair
        interval = self.interval
   

        current_date = current_date.strftime('-%Y-%m-%d')

        # file = pair+'-'+interval+current_date+'.csv'
        file = pair+'-'+interval+current_date+'.pkl'
        m_file = 'm'+file

        file = path+file
        m_file = path+m_file

        return file, m_file

    def _make_file_names_new(self):
    

            path = self.path
            
            # file = pair+'-'+interval+current_date+'.csv'
            file = 'datastore.pkl'
            m_file = 'marks.pkl'

            file = path+file
            m_file = path+m_file

            return file, m_file

    def _calculate_data_span(self, candle_count, period):
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





