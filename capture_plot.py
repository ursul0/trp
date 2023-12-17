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
import threading

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

PERIOD_ENM = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', \
              '12h', '1d', '3d', '1w', '1M']
SYMBOL_ENM = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT']

DEBUG_PRINT = 0



class CaptureOnClick:
    """ interactive plot, chart marking data collector """
    def __init__(self, path = '.\\.data\\', pair_df=None, data_proc:DataProc = None, \
                 symbol='BTCUSDT', interval='1m'):
        # self.fig = mpf.figure(style='yahoo',figsize=(10,6))
        self.fig = mpf.figure(style='charles',figsize=(10,6))
        self.ax  = self.fig.add_subplot()   
        # self.fig, (self.ax, self.ui_ax) = plt.subplots(2, 1, figsize=(10, 8),\
        #  gridspec_kw={'height_ratios': [4, 1]})
        # fig, ax = plt.subplots(figsize=(10, 6))
     
        self.path = path
        self.pair = symbol
        self.interval = interval

        #initialize data processor
        if data_proc is None:
            "Provide DataProc object for data processing."
        else:
            self.data_proc = data_proc

        if pair_df is None:
            self.pair_df, self.m_file = self.data_proc.get_new_data(self.pair, self.interval,True)
        else:     
           self.pair_df = pair_df
        
        self.filename, _ = self.data_proc._make_file_names()
        
        #debug print
        self.captured_output = ''
        
        # self.RefreshThread = INTupdateThread(plotter = self)

        # Markings:
        self.marks = []
        #TODO maybe: # self.marks =  pd.DataFrame()

        self.run_refresh_flag = False
               
        # self.ax.set_ylabel('price')
        # self.ax.set_xlabel('time')
        self.ax.set_title(f'Interactive chart of {self.pair}')
              
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_pick)
        # def disconnect_callback(self):
        #     # Disconnect the callback using the connection id
        #     self.fig.canvas.mpl_disconnect(self.cid)

        # Add textboxes below the axes
        # Adjust the position of the axes to leave space for the textboxes
        # pos :             [left, bottom, width, height] 
        self.ax.set_position([0.03, 0.22, 0.88, 0.73])
        

        # Add textboxes below the axes
        textbox_pair_pos = [0.15, 0.015, 0.12, 0.05]
        textbox_period_pos = [0.4, 0.015, 0.05, 0.05]
        self.tb_pair = TextBox(plt.gcf().add_axes(textbox_pair_pos), 'Pair:', \
                               initial=self.pair)
        self.tb_period = TextBox(plt.gcf().add_axes(textbox_period_pos), 'Period:', \
                                 initial=self.interval)
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
 
        # Create CheckButtons widget
        # self.checkbox_ax = plt.axes([0.88, 0.01, 0.1, 0.05])  #  position and size
        # self.checkbox = CheckButtons(self.checkbox_ax, labels=['INT'], actives=[False])
        # self.checkbox.on_clicked(self.on_checkbox_clicked)


        self.update_plot()
     
        plt.show()

    def refresh_plot_data(self):   
        self.pair_df, self.pair, self.interval = self.data_proc._append_data()
        return pd.to_datetime(self.pair_df.index[-1]) #same as .tail(1)
        # sleep(TPC)
        
    def _clear_marks_from_plot(self):
        try:
            for mark_entry in self.marks:
                obj_cl = mark_entry[7]  
                obj_cl.remove() 
        except IndexError:
            pass  
        self.ax.figure.canvas.draw()

# date, x, y, old_m_idx, e_w, e_h, buy 
# ['Date'], ['x'],['y'],['m_idx'], ['ecl_w'], ['ecl_h'] ,['buy']
               
    def _add_marks2plot(self):
        if len(self.marks) > 0:
            try:
                for mark_entry in self.marks:
                    obj_cl = mark_entry[7]  
                    self.ax.add_patch(obj_cl)
            except IndexError:
                pass  

        self.ax.figure.canvas.draw()

    def _redraw_marks(self):
        self.marks_resync_flag = True
        self._clear_marks_from_plot()
        #sync here?1?
        self._add_marks2plot()
        
        self.ax.figure.canvas.draw()




    #update plot, also from refresher task: INTupdateThread
    def update_plot(self, live = False):
        if hasattr(self, 'ax'):

            self.ax.clear() 
            mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500) 
            # self._add_marks2plot()
            # plt.pause(TPC/100)
            self.ax.figure.canvas.draw()
            # plt.show()

        #reset flags after plot update

    def redraw_plot(self):
        self.ax.clear()
        self.ax.set_title(f'Interactive chart of {self.pair}')
        #add marks to the plot
        mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500) 
        self.load_and_plot_m_from_file()
        self.ax.figure.canvas.draw()
        
    #OK
    def add_rmv_plot_mark(self, event):
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
                        # self.captured_output += f' date clicked: {date_clicked} '
                        # self.captured_output += f' figure coords: ({event.x}, {event.y})'
                        
                        #get current location, TODO some old func, review
                        #add marks to self.marks & plot on axes
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
            
            self.add_rmv_plot_mark(event)

        else:
            self.captured_output += f'Figure clicked at: ({event.x},{event.y}) | '

    
    def on_tb_pair_submit(self, text): 
        if text == self.pair:
            self.captured_output += f"{self.pair} reconfirmed. | "
            if DEBUG_PRINT == 1:
                print(self.captured_output)
                # self.redraw_plot()
        else:
            self.pair = text
            self.captured_output += f"Getting {self.pair} {self.interval} data... | "
            if DEBUG_PRINT == 1:
                print(self.captured_output )
            td_idx_last = self._refresh_plot_data()
            self.captured_output += f"Loaded up to: {pd.to_datetime(td_idx_last)} | "
            if DEBUG_PRINT == 1:
                self.captured_output
              
        # self.data_refresh_flag = False
        # self.update_plot() 
    
    def on_tb_period_submit(self, text): 
        if text == self.interval:
             self.captured_output += f"{self.interval} reconfirmed. | "
             if DEBUG_PRINT == 1:
                print(self.captured_output)
                # self.redraw_plot()
        else:
            self.interval = text
            self.captured_output += f"Getting {self.pair} {self.interval} data... | "
            if DEBUG_PRINT == 1:
                    print(self.captured_output)
            td_idx_last = self.refresh_plot_data()
            self.captured_output += f"Loaded up to: {pd.to_datetime(td_idx_last)} | "
            if DEBUG_PRINT == 1:
                print(self.captured_output )

        # self.data_refresh_flag = False 
        self.update_plot()
        
    def on_get_data_button_click(self, event):
        ev_name = event.name
        if ev_name == 'button_release_event':
            last_entry_idx = self.refresh_plot_data()
            self.data_refresh_flag = True
            self.update_plot()
            self.captured_output += f'New data up to: {last_entry_idx} | '
            if DEBUG_PRINT == 1:
                print (self.captured_output)

    def on_save_data_button_click(self, event):
        # x_coord = event.xdata
        # y_coord = event.ydata  
        ev_name = event.name
        if ev_name == 'button_release_event':
            # if event.inaxes == self.ax:
            self.save_m_to_file()
            self.captured_output += f'Saved marks data in: {self.m_file} | '
            if DEBUG_PRINT == 1:
                print (self.captured_output)


    def on_checkbox_clicked(self, label):
        if label == 'INT':
            if self.checkbox.get_status()[0]:
                self.captured_output += "Now interactive mode is ON. "
                self.RefreshThread.run()
                self.run_refresh_flag = True
            else:
                # deselected: Stop the INTupdateThread when interactive mode is turned off
                self.RefreshThread.stop()  
                self.run_refresh_flag = False
                self.captured_output += "Now interactive mode is OFF. "
        self.update_plot()

    def euclidean_distance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

    def save_m_to_file(self):
        # Save selected points to a CSV file
        # self.filename
        df = pd.DataFrame(self.marks, columns=['Date', 'x', 'y', 'm_idx', 'ecl_w', 'ecl_h', 'buy', 'ellipse'])
        df.to_csv(self.m_file, index=False)

    def load_and_plot_m_from_file(self):
        # Check if the file exists before loading
        if os.path.exists(self.m_file):
            # Load selected points from a CSV file
            df = pd.read_csv(self.m_file)

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
            # print(f"File '{self.m_file}' does not exist. No points loaded.")
            self.captured_output = f"File '{self.m_file}' does not exist. No points loaded."
            if DEBUG_PRINT == 1:
                print(self.captured_output)
    #fixes y locations for 

    def draw_MA(self):
        # This is just a placeholder function, you can customize it to draw something on the chart
        # self.captured_output = "should draw ma on the chart"
        mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500, mav=(50,21,7))
    def remove_MA(self):
        # This is just a placeholder function, you can customize it to remove the drawing
        # self.captured_output = "should remove ma from the chart"
        self.ax.clear()
        mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500)
   

class INTupdateThread(Thread):
    def __init__(self, plotter):
        super(INTupdateThread, self).__init__()
        self.plotter = plotter
        self.stop_event = threading.Event()

    def run(self):
        try:
            while not self.stop_event.is_set():
                self.plotter.update_plot()
                sleep(1)
        except Exception as e:
            # Handle exceptions here or log them
            print(f"Thread Error: {e}")
        finally:
            print("Thread Exiting...")

    def stop(self):
        self.stop_event.set()
        


