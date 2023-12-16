import matplotlib.pyplot as plt
import mplfinance as mpf

import pandas as pd
import numpy as np

import os
from time import sleep

# from threading import Timer

import datetime as dt
import matplotlib.dates as mdates

from matplotlib.widgets import Button, CheckButtons
from matplotlib.widgets import TextBox, RadioButtons 
import matplotlib.patches as patches 

from threading import Thread

# from matplotlib.animation import FuncAnimation
# if not hasattr(mpf, 'animation'):
#     raise ImportError("mplfinance version doesn't support animation. Please update mplfinance.")

# from data_proc import get_new_data, make_file_names
from data_proc import DataProc

# import mplcursors
#%matplotlib inline
#   %matplotlib widget
#%matplotlib notebook

# from matplotlib.widgets import Dropdown
# from ipywidgets import widgets



#up to 2500?
TOTAL_CANDLES_ON_THE_SCREEN = 100
TPC = 100
MARK_WIDTH = 1.5

PERIOD_ENM = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
SYMBOL_ENM = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT']

DEBUG_PRINT = 1



class CaptureOnClick:
    """ interactive plot, chart marking data collector """
    def __init__(self, pair_df=None, data_proc:DataProc = None, pair='BTCUSDT', period='1m'):
        # fig = mpf.figure(style='yahoo',figsize=(10,6))
        self.fig = mpf.figure(style='charles',figsize=(10,6))
        self.ax  = self.fig.add_subplot()    
        self.data_proc = data_proc

        # self.fig, (self.ax, self.ui_ax) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [4, 1]})
        # fig, ax = plt.subplots(figsize=(10, 6))
        self.pair = pair
        self.period = period
        self.filename, self.m_filename = None, None

        # self.data_proc.make_file_names(self.pair,self.period)
        
        # pair ochl+volume data
        self.pair_df = pair_df  
        #debug print
        self.captured_output = ''
        
        # self.RefreshThread = None
        self.RefreshThread = INTupdateThread(plotter = self)
       
        # Markings:
        self.marks = []
        #TODO:
        # self.marks =  pd.DataFrame()

        #flags on init:
        if pair_df == None:
            self.data_refresh_flag = True
        
        self.marks_resync_flag = False
        self.run_refresh_flag = False
       
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = True
        
        # self.ax.set_ylabel('price')
        # self.ax.set_xlabel('time')
        self.ax.set_title(f'Interactive chart of {self.pair}')
              
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_pick)

        # Add textboxes below the axes
        # Adjust the position of the axes to leave space for the textboxes
        # pos :             [left, bottom, width, height] 
        self.ax.set_position([0.03, 0.22, 0.88, 0.73])
        

        # Add textboxes below the axes
        textbox_pair_pos = [0.15, 0.015, 0.12, 0.05]
        textbox_period_pos = [0.4, 0.015, 0.05, 0.05]
        self.tb_pair = TextBox(plt.gcf().add_axes(textbox_pair_pos), 'Pair:', initial=self.pair)
        self.tb_period = TextBox(plt.gcf().add_axes(textbox_period_pos), 'Period:', initial=self.period)
        # Connect events to the textboxes
        self.tb_pair.on_submit(self.on_tb_pair_submit)
        self.tb_period.on_submit(self.on_tb_period_submit)

        # button to get new data
        button_pos = [0.65, 0.015, 0.1, 0.05] 
        self.get_data_btn = Button(plt.gcf().add_axes(button_pos), 'Get Data')
        self.get_data_btn.on_clicked(self.on_get_data_button_click)

        # button to save markings
        button_pos = [0.77, 0.015, 0.1, 0.05] 
        self.save_data_btn = Button(plt.gcf().add_axes(button_pos), 'Save Marks')
        self.save_data_btn.on_clicked(self.on_save_data_button_click)

        # button to remove all markings
        # pos :    [left, bottom, width, height] 
        # button_pos = [0.54, 0.015, 0.1, 0.05] 
        # self.get_data_btn = Button(plt.gcf().add_axes(button_pos), 'Clear MArks')
        # self.get_data_btn.on_clicked(self.on_clear_marks_button_click)

        # ax.xaxis_date(tz=None)
        # ax.xaxis_date()
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  
        # Adjust the format as needed
     
        # Create CheckButtons widget
        self.checkbox_ax = plt.axes([0.88, 0.01, 0.1, 0.05])  #  position and size
        self.checkbox = CheckButtons(self.checkbox_ax, labels=['INT'], actives=[False])
        self.checkbox.on_clicked(self.on_checkbox_clicked)
       

        # mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500)
        # plt.show()

        # pass CaptureOnclick plot object to the data updater thread
        # _int_update_thread_function(self)
       
        self.update_plot()

    #update plot, also from refresher task: INTupdateThread
    def update_plot(self, live = False):
        
        # cur_sngl_row = pd.DataFrame()
        # sleep(TPC)

        if hasattr(self, 'ax'):
            # Implement the logic to refresh the plot in the main thread
            # This might involve clearing the axes, re-plotting data, etc.

            #parse flags 
            if self.data_refresh_flag == True:  
                self.marks.clear()
                self.ax.clear()
                self.pair_df, self.m_filename  = \
                self.data_proc.get_new_data(self.pair, self.period)

                self.ax.set_title(f'Interactive chart of {self.pair}')
                #add marks to pthe lot
                        
                self.load_and_plot_m_from_file()
                self.data_refresh_flag = False
                self.marks_resync_flag = False

 
        mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500)         
        plt.pause(TPC/100)
        self.fig.canvas.flush_events()
        plt.show()



        #reset flags after plot update

        

    def add_plot_mark(self, event):
        # if event.inaxes is not None:
        if event.inaxes == self.ax:
            #get data coordinates:
            x_coord = event.xdata
            y_coord = event.ydata
            #figure? coordinates : event.x, event.y

            if x_coord is not None and y_coord is not None:
                valid_x_range = self.pair_df.shape[0]
      
                if 0<= x_coord < valid_x_range:

                    if event.key == 'shift' and event.button == 1:
                        # Shift + Left click: Remove the nearest ellipse on axes
                        if self.marks:
                            distances = [self.euclidean_distance((x_coord, y_coord), (point[1], point[2])) for point in self.marks]
                            nearest_ellipse_index = distances.index(min(distances))
                            # Remove the corresponding patch 
                            _, _, _, _, _, _, _, ellipse_to_remove = self.marks.pop(nearest_ellipse_index)
                            ellipse_to_remove.remove()

                    elif event.button == 1 or event.button == 3:
                        # Left or Right click: Draw an ellipse 
                        ax_h_end = self.ax.get_ylim()[1]
                        ax_h_st = self.ax.get_ylim()[0]
                        ax_w = self.ax.get_xlim()[1] 

                        ax_h = ax_h_end - ax_h_st

                        h2w_factor = ax_h / ax_w  

                        ecl_w = MARK_WIDTH
                        ecl_h = h2w_factor  * 10/6 #ratio

                        #capture the user input
                        self.captured_output = f"Data coords: ({x_coord}, {y_coord})"            
                        date_clicked = self.pair_df.index[round(x_coord)] 
                        self.captured_output += f' date clicked: {date_clicked} '
                        self.captured_output += f' figure coords: ({event.x}, {event.y})'
                        if DEBUG_PRINT == 1:
                            print(self.captured_output)

                        m_candle_idx = self.pair_df.index.get_loc(date_clicked)
            
                        color = 'green' if event.button == 1 else 'red'
                        ellipse = patches.Ellipse((x_coord, y_coord), width=ecl_w, height=ecl_h, angle=0, color=color, fill=False)
                        buy = 1 if event.button == 1 else 0
                        self.marks.append((date_clicked, x_coord, y_coord, m_candle_idx, ecl_w, ecl_h, buy, ellipse))
                        self.ax.add_patch(ellipse)

                    self.ax.figure.canvas.draw()
                else:
                    self.captured_output ="Clicked outside the valid range of indices"
            else:
                self.captured_output ="Invalid click coordinates"
        # Click occurred outside the axes
        else:
            self.captured_output ="Clicked outside the axes"   
        
        if DEBUG_PRINT == 1:
            print(self.captured_output)



    #handle UI events
    def on_pick(self, event):
        # Check if the pick event occurred on the plot_ax or ui_ax
        if event.inaxes == self.ax:
            if DEBUG_PRINT == 1:
                print("Click event on plot axes")
            self.add_plot_mark(event)
            #set flags 
            # self.run_refresh_flag
            self.update_plot()
    
    def on_tb_pair_submit(self, text): 
        if text == self.pair:
            self.data_refresh_flag = False
        else:
            self.data_refresh_flag = True
        self.pair = text
        self.update_plot() 
    
    def on_tb_period_submit(self, text): 
        if text == self.period:
            self.data_refresh_flag = False
        else:
            self.data_refresh_flag = True 
        self.period = text
        self.update_plot()

    def on_get_data_button_click(self, event):
        self.data_refresh_flag = True
        self.update_plot()

    def on_save_data_button_click(self, event):
        self.save_m_to_file()

    def on_checkbox_clicked(self, label):
        if label == 'INT':
            if self.checkbox.get_status()[0]:
                if DEBUG_PRINT == 1:
                    print("Now interactive mode is ON")
                self.RefreshThread.start() 

            else:
                # Checkbox is deselected
                if DEBUG_PRINT == 1:
                    print("Interactive mode is OFF")
                # (4) Stop the INTupdateThread when interactive mode is turned off
                self.RefreshThread.stop()   
        self.update_plot()

    def resync_marks(self):
        self.marks_resync_flag = True
        self.update_plot()




    def euclidean_distance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

    def save_m_to_file(self):
        # Save selected points to a CSV file
        # self.filename
        df = pd.DataFrame(self.marks, columns=['Date', 'x', 'y', 'm_idx', 'ecl_w', 'ecl_h', 'buy', 'ellipse'])
        df.to_csv(self.m_filename, index=False)

    def load_and_plot_m_from_file(self):
        # Check if the file exists before loading
        if os.path.exists(self.m_filename):
            # Load selected points from a CSV file
            df = pd.read_csv(self.m_filename)

            # #draw markings from the saved overlay, fix locations on the timeline
            for index, row in df.iterrows():
                date, x, y, old_m_idx, e_w, e_h, buy = row['Date'], row['x'], row['y'], row['m_idx'], row['ecl_w'], row['ecl_h'] ,row['buy']
                color = 'green' if buy == 1 else 'red'

                m_candle_time = pd.to_datetime(date)
                try:
                    new_m_candle_idx = self.pair_df.index.get_loc(m_candle_time)
                    shift = old_m_idx - new_m_candle_idx
                    x-=shift
                except KeyError:
                    if DEBUG_PRINT == 1:
                        print(f"Candle at {m_candle_time} is out of bounds.")
                    self.captured_output = f"Candle at {m_candle_time} is out of bounds."
                    continue
                else:
                    ellipse = patches.Ellipse((x, y), width=e_w, height=e_h, angle=0, color=color, fill=False)
                    self.marks.append((date, x, y, new_m_candle_idx, e_w, e_h, buy, ellipse))
                    self.ax.add_patch(ellipse)
                
                # first_item_start_time = str(df['Date'][0])
                # first_item_start_time_n = mdates.datestr2num(first_item_start_time)
                # first_item_start_time_d = mdates.num2date(first_item_start_time_n)
                # first_item_start_time= pd.to_datetime(first_item_start_time)
                
        else:
            # print(f"File '{self.m_filename}' does not exist. No points loaded.")
            self.captured_output = f"File '{self.m_filename}' does not exist. No points loaded."
            if DEBUG_PRINT == 1:
                print(self.captured_output)
    #fixes y locations for 
    def sync_marks_on_pair(self):
            df= self.pair_df
            nm = []
            for m in self.marks:
                # if df.index[TOTAL_CANDLES_ON_THE_SCREEN-1] != m['0']:
                    try:
                        date=pd.to_datetime(m[0])

                        idx_in_nd = round(df.index.get_loc(date))
                        idn_in_od = round(m[3])
                        # if idx_in_nd != idn_in_od:
                        #     y=nd[2]

                        # (date, x, y, new_m_candle_idx, e_w, e_h, buy, ellipse)
                        
                        #get target y from updated plot data
                        # same interval, fixed num of candles- should be fine
                        #TODO check the ABOVE
                        nd = df.loc[idx_in_nd]

                        color = 'green' if m[6] == 1 else 'red'

                        y=nd[2]  #candle/target y
                        x=nd[1]  #candle/target y
                        e_w = m[4]
                        e_h= m[5]

                        #tests
                        # #===============================
                        # t_dn = nd[0]  #candle date
                        # t_do = m[0]  #mark date
                        # if t_dn == t_do:
                        #     print(f'synced mark at: {t_do}, coord: ({x}, {y})')
                        # else:
                        #     print("Cant sync marks")
                        #     break
                        #tests
                        #===============================
                       
                       #plot  markings
                        ellipse = patches.Ellipse((x, y), width=e_w, height=e_h, angle=0, color=color, fill=False)
                        self.ax.add_patch(ellipse)
                        #prepare new markings list
                        nm.append((date, x, y, idx_in_nd, e_w, e_h, m[6], ellipse))
                        
                        
                    except KeyError:
                        # print(f"Candle at {m_candle_time} is out of bounds.")
                        self.captured_output = f"Candle at {date} is out of bounds."
                        if DEBUG_PRINT == 1:
                            print(self.captured_output)
                        continue
                # else:
                # nm.append((m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],))
            self.pair_df = nm

            if DEBUG_PRINT == 1:
                print(self.captured_output)
       
                
        

    def draw_MA(self):
        # This is just a placeholder function, you can customize it to draw something on the chart
        # self.captured_output = "should draw ma on the chart"
        mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500, mav=(50,21,7))
    def remove_MA(self):
        # This is just a placeholder function, you can customize it to remove the drawing
        # self.captured_output = "should remove ma from the chart"
        self.ax.clear()
        mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500)
   
    def update_dataframe(self):
        # Update DataFrame with 'buy' hot bit
        # self.pair_df['buy'] = 0

        for point in self.marks:
            m_time, x, y, _,_,_,_,_ = point
          
            ##TO_DO: mark / prepare data
            # mask = (self.pair_df['time'] >= x) & (self.pair_df['time'] <= x)  # Adjust based on your DataFrame columns     
            # self.pair_df.loc[mask, 'buy'] = buy
 


#global function for plot auto refresh/update_plot thread 
def _int_update_thread_function(plotter:CaptureOnClick):
    while plotter.run_refresh_flag == True:
           plotter.update_plot(live=True)
           sleep(TPC*5)

#thread for Plot auto refresh/update_plot calls
class INTupdateThread(Thread):
    def __init__(self, plotter):
        super(INTupdateThread, self).__init__()
        self.plotter= plotter

    def start(self):
        self.plotter.run_refresh_flag = True
        _int_update_thread_function(self.plotter)

    def stop(self):
         self.plotter.run_refresh_flag = False

