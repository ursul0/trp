
from data_proc import DataProc
from capture_plot import CaptureOnClick
import pandas as pd
from time import sleep
# from datetime import datetime, timedelta
# import os
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT']
TOTAL_CANDLES = 100
SYMBOL = 'BTCUSDT'
INTERVAL ='1m'

#======================================================

dp = DataProc('.\\.data\\0.05a\\')

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

# 18-Dec-2023:
#TODO add custom interval from UI + selection/mechanism to set different TOTAL_CANDLES
#TODO implement save marks removes marks!!!
#TODO review marks resync(store) mechanism (file vs local store/define on_interval_change functionality)
#TODO add sessions (/trades) + auto populate
#TODO check of on _refresh more then 1 is needed


#TODO review flags & thread 


#TODO last public release ====
#TODO fork into private repo
#TODO add order process/aquire/config/display/track


while(1):
    sleep(1)


# plotter = CaptureOnClick()




# Save points to file
# plotter.save_m_to_file()


print("Done!")


#======================================================
'''# Perform operation on a single entry in the target DataFrame
target_timestamp = pd.to_datetime('2022-01-01 14:15:00')  # Replace with your specific timestamp
merged_df = pd.merge_asof(target_df, source_df, on='Timestamp', direction='nearest')

# Assuming you want to perform an operation (e.g., addition) on the matched entries
merged_df['Result'] = merged_df['Value_Target'] + merged_df['Value_Source']




'''