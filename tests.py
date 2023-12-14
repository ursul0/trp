
from data_proc import DataProc
from capture_plot import CaptureOnClick

from datetime import datetime, timedelta
import os

# REFRESH_INPUT_DATA = 1
# # =====================================

# TOTAL_CANDLES = 100
# SYMBOL = 'SOLUSDT'
# INTERVAL ='1m'

# # =====================================

# current_datetime = datetime.today()
# current_date = current_datetime.date()  # Extract date from datetime
# current_date_0h = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

# #get 3 days back from today
# MAX_DAYS_TO_GET_BACK = 1
# current_date_0h -= timedelta(days=MAX_DAYS_TO_GET_BACK)

# # getting the timestamp for binance format
# # current_date_0h= datetime.fromisoformat('2023-12-06 00:00:00')
# t_start = int(datetime.timestamp(current_date_0h)*1000)

# tc= '-'
# filename = SYMBOL+tc+INTERVAL+current_date.strftime('-%Y-%m-%d')+'.csv'

# path = '.\\.data\\'
# if not os.path.exists(path+filename) or REFRESH_INPUT_DATA:
#     # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
#     pair_df= get_historic_data(symbol=SYMBOL, timestamp=t_start, interval=INTERVAL, filename=path+filename)
    
#     #pair_df = get_all_historic_data(symbol=SYMBOL, interval=INTERVAL, filename=path+filename)
#     pair_df = pair_df[-TOTAL_CANDLES:] #get only latest TOTAL_CANDLES entries
# else:
#     pair_df = read_data_tail(path+filename, TOTAL_CANDLES)

# #print(pair_df)

# plt_filename = path+'m'+ filename
# TOTAL_CANDLES = 100
# SYMBOL = 'BTCUSDT'
# INTERVAL ='1m'




# pair_df, _, _ = dtata_processor.get_new_data(TOTAL_CANDLES, SYMBOL,INTERVAL)
# Load points from file and continue editing
# plotter = CaptureOnClick(pair_df, SYMBOL, INTERVAL)


dtata_processor = DataProc('.\\.data\\ntb\\')
pair_df, _, _ = dtata_processor.get_new_data()
plotter = CaptureOnClick(pair_df, dtata_processor)

# Save points to file
# plotter.save_m_to_file()


print("Done!")

