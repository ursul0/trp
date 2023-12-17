
from data_proc import DataProc
from capture_plot import CaptureOnClick

# from datetime import datetime, timedelta
# import os

# TOTAL_CANDLES = 100
# SYMBOL = 'BTCUSDT'
# INTERVAL ='1m'

#======================================================

data_processor = DataProc('.\\.data\\')
plotter = CaptureOnClick(data_proc=data_processor)


# plotter = CaptureOnClick()




# Save points to file
# plotter.save_m_to_file()


print("Done!")


#======================================================