
from data_proc import DataProc, DEF_SYMBOL, DEF_INTERVAL, SYMBOLS, INTERVALS
from capture_plot import CaptureOnClick
import pandas as pd
from time import sleep


# 18-Dec-2023:
#TODO move marks to df = DONE
#TODO implement save marks removes marks!!! = DONE

#TODO: make space for the future

#TODO: horisontal rays
#TODO: lines

#TODO add custom interval from UI + selection/mechanism to set different TOTAL_CANDLES

#TODO review marks resync(store) mechanism (file vs local store/define on_interval_change functionality)
#TODO add sessions (/trades) + auto populate
#TODO check of on _refresh more then 1 is needed

#TODO add tests

#TODO review flags & thread 


#TODO last public release ====
#TODO fork into private repo
#TODO add order process/aquire/config/display/track


def main():
    
    dp = DataProc('.\\.data\\v0.0504a\\')
    plotter = CaptureOnClick(data_proc=dp)

    # while(1):
    #     sleep(1)

    # print("Done!")

    # Save points to file
    # plotter._save_m_to_file()
    del plotter
    del dp

if __name__ == "__main__":
    main()









