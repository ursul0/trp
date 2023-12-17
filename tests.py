
from data_proc import DataProc
from capture_plot import CaptureOnClick
import pandas as pd
# from datetime import datetime, timedelta
# import os

TOTAL_CANDLES = 100
SYMBOL = 'BTCUSDT'
INTERVAL ='1m'

#======================================================

dp = DataProc('.\\.data\\0.05a')

# #datamap initialized with two entries: BTCUSDT and ETHUSDT, each may hold candles data in corresponding interval from INTERVALS 
# datamap = pd.DataFrame(dp.data_map)

# #data is accumulated here, (TODO:and updated when needed )
# datastore = pd.DataFrame(dp.pair_df_store)

# #get one TOTAL_CANDLES set of OCHL+Volume for 
# pair_df = pd.DataFrame(datastore['BTCUSDT']['1m'])

# #default load:
# last_updated = datamap['BTCUSDT']['1m']['Updated']
# start_date = datamap['BTCUSDT']['1m']['StartDate']
# end_date = datamap['BTCUSDT']['1m']['EndDate']

# total_candles = pd

# print (f'\nwe have: {TOTAL_CANDLES} candles of {dp.pair} at {dp.interval} loaded on {last_updated} between dates: {start_date}-{end_date} \n')
# print(datamap.shape, datastore.shape, pair_df.shape, '\n')
# print(pair_df.index[0:5], '\n')
# print(pair_df[0:5], '\n')



plotter = CaptureOnClick(data_proc=dp)







# plotter = CaptureOnClick()




# Save points to file
# plotter.save_m_to_file()


print("Done!")


#======================================================