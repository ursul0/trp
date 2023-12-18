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

from data_proc import DataProc



#up to 2500?
TOTAL_CANDLES = 100
TPC = 100
MARK_WIDTH = 1.5
# SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT']
# PERIODS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']

INTERVALS_ON_APPEND = 1

DEBUG_PRINT = 1



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
            print("Provide DataProc object.")
            return
        else:
            self.dp = data_proc

        # self.pair_df = pd.DataFrame(self.data_proc.pair_df).copy(deep=True)
        self.pair_df = self.dp.pair_df
        
        #TODO move all file operations away?
        self.file, self.m_file = self.dp._make_file_names()
        
        #debug print
        self.captured_output = ''
        
        #initialize 
        self.f_new_plot_data = False
        # self.RefreshThread = INTupdateThread(plotter = self)

        # Markings:
        self.marks = []
        #TODO maybe: # self.marks =  pd.DataFrame()
        

        
        #TODO: in case we want to update old marks a new interval on the same pair
        self.f_marks_resync = False
        # self.f_marks_redraw = False

        # self.run_refresh_flag = False
               
        # self.ax.set_ylabel('price')
        # self.ax.set_xlabel('time')
        self.ax.set_title(f'Interactive chart of {self.pair} {self.interval}')
              
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
        textbox_interval_pos = [0.4, 0.015, 0.05, 0.05]
        self.tb_pair = TextBox(plt.gcf().add_axes(textbox_pair_pos), 'Pair:', \
                               initial=self.pair)
        self.tb_interval = TextBox(plt.gcf().add_axes(textbox_interval_pos), 'Period:', \
                                 initial=self.interval)
        
        
        # self.tb_pair.active = False
        # self.tb_interval.active = False

        # Connect events to the textboxes
        # self.tb_pair.on_submit(self.on_tb_pair_submit())
        # self.tb_interval.on_submit(self.on_tb_interval_submit)

         # Connect events to the textboxes
        self.tb_pair.on_submit(lambda text: self.on_tb_pair_submit(text, self.event))
        self.tb_interval.on_submit(lambda text: self.on_tb_interval_submit(text, self.event))



        

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
        self.event = None

        # no_pasaran_flag = True

        self.get_plot_data()
        self._draw_plot()
        plt.show()
        # self.ax.figure.show()

    def get_plot_data(self):   
        pair_df, pair, interval = self.dp.get_new_data(self.pair, self.interval, False)
        # sleep(0.01)
        self.pair_df = pair_df#.copy(deep=True)

        return pd.to_datetime(self.pair_df.index[-1]) 
    
    def refresh_plot_data(self):   
        pair_df, pair, interval = self.dp.append_data(self.pair, self.interval)
        self.pair_df = pair_df    #.copy(deep=True) if we want to allocate a copy
        #returns datetime of the data tail entry (last candle data time)
        return pd.to_datetime(self.pair_df.index[-1])
        
        
    def _clear_marks_from_plot(self):
        try:
            for mark_entry in self.marks:
                obj_cl = mark_entry[7]  
                obj_cl.remove() 
        except IndexError:
            pass  

    def load_and_plot_m_from_file(self):
        #TODO: remove all file operations from the class
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

    def _add_marks2plot(self):
        if len(self.marks) > 0:
            try:
                for mark_entry in self.marks:
                    obj_cl = mark_entry[7]  
                    # DataFrame(self.marks, columns=['Date', 'x', 'y', 'm_idx', 'ecl_w', 'ecl_h', 'buy', 'ellipse'])

                    # ax_h_end = self.ax.get_ylim()[1]
                    # ax_h_st = self.ax.get_ylim()[0]
                    # ax_w = self.ax.get_xlim()[1] 
                    # ax_h = ax_h_end - ax_h_st
                    # h2w_factor = ax_h / ax_w  
                    # ecl_w = MARK_WIDTH
                    # ecl_h = h2w_factor  * 10/6 #ratio
                    # buy = 1 if color == 'green' else 0
                                 
                    # color = 'green' if event.button == 1 else 'red'
                    # 
                    # ellipse = patches.Ellipse((x_coord, y_coord), width=ecl_w, height=ecl_h, angle=0, color=color, fill=False)
                    
                    self.ax.add_patch(obj_cl)
            except IndexError:
                pass  
            # plt.draw()
      
    def _redraw_marks(self):
        # self.marks_resync_flag = True
        self._clear_marks_from_plot()
        #sync here?1?
        self._add_marks2plot()
        # plt.draw()
   
    #update plot,  from refresher thread
    def _t_update_plot(self):

        # if hasattr(self, 'ax'):
            if self.f_marks_resync == True:
                self._redraw_marks()
                self.f_marks_resync = False
                # plt.draw()

            if self.f_new_plot_data== True:
                self._redraw_plot()
                self.f_new_plot_data== False

            self._update_plot_text()
            self.ax.figure.canvas.draw()
                           

    def _replot_data_and_marks(self):
            self._redraw_plot()
            self.ax.clear() 
            mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500) 
            #resync and add marks
            self.load_and_plot_m_from_file()
        

    def _draw_plot(self):
        
        # if self.f_new_plot_data != True: 
            mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500) 
            self.load_and_plot_m_from_file()
            self.ax.set_title(f'Interactive chart of {self.pair} {self.interval}')
            self.ax.figure.canvas.draw()
            # plt.show()
        # else:
        #     print("WTF?")
            
    def _redraw_plot(self):
        #TODO reveiew and rewrite
        
        
        # no check if empty(why would it be?) and has last candle only
        if self.pair_df.shape[0] == TOTAL_CANDLES:
            #draw new data, including new interval
            self.ax.clear()
            mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500) 
            self.load_and_plot_m_from_file()
            
          
        elif self.pair_df.shape[0] == INTERVALS_ON_APPEND:
            #TODO: update only the last candle, not whole plot 


            #update last v-line/candle on a plot
            mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500)
            
            # line.set_xdata([updated_position])
            print('update last line on a plot!!!')
        else:
            print('_redraw_plot: WTF?')
            
            #

            
     
        # self.ax.set_title(f'Interactive chart of {self.pair} {self.interval}')        
        # self.ax.figure.canvas.draw()
        
        # plt.draw()

    def _update_plot_text(self):
        self.ax.set_title(f'Interactive chart of {self.pair} {self.interval}')
        self.tb_pair.set_val(self.pair)
        self.tb_interval.set_val(self.interval)




    #Plot interactions:
    def add_rmv_plot_mark(self, event):
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
                            distances = [self._eucl_distance((x_coord, y_coord), (point[1], point[2])) for point in self.marks]
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
                        buy = 1 if color == 'green' else 0
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
        self.event = event
        if event.inaxes == self.ax:
            #     print("Click event on plot axes")
            self.add_rmv_plot_mark(event)
        else:
            self.captured_output += f' on_pick(): Figure clicked at: ({event.x},{event.y}) | '
            if event.key is not None:
                print(event)


    
    def on_tb_pair_submit(self, text, event): 
        if event.name != 'button_release_event' and event.key != '\r':
            return

        else:
            if text == self.pair:
                last_dta_time = pd.to_datetime(self.refresh_plot_data())
                self.captured_output += f'Added up to: {last_dta_time}'
                #TODO: make only one vline update now
                self.f_new_plot_data= True
                # self.f_marks_resync = False  
                self._t_update_plot() 
            else:
                self.pair = text #self.tb_pair.text
                self.interval = self.tb_interval.text
                last_dta_time = pd.to_datetime(self.get_plot_data())
                self.captured_output += f'Loaded up to: {last_dta_time}'
                self.f_new_plot_data= True
                # self.f_marks_resync = True  
                self._t_update_plot() 

            if DEBUG_PRINT == 1:
                print(self.captured_output)
    
    def on_tb_interval_submit(self, text, event): 
        if event.name != 'button_release_event' and event.key != '\r':
            return

            #  text_box = TextBox(ax, label="Period:", initial="10")
            #  if fig.canvas.manager.key_press_handler_id == text_box.submit_ctx.id:
            # self.tb_pair = TextBox(plt.gcf().add_axes(textbox_pair_pos), 'Pair:', initial=self.pair)
        # if self.fig.canvas.manager.key_press_handler_id == self.tb_pair.submit_ctx.id: 
        else:  
            if text == self.interval:
                self.interval = text #self.tb_pair.text
                last_dta_time = pd.to_datetime(self.refresh_plot_data())
                #TODO: make only one vline update now
                self.captured_output = f'Reconfirmed interval: {self.interval}'
                self.captured_output += f' Added up to: {last_dta_time}'
                self.f_new_plot_data= False
                # self.f_marks_resync = False  
                self._t_update_plot() 
                
            else:
                #get both textboxes:
                self.interval = text
                self.pair = self.tb_pair.text
                last_dta_time = pd.to_datetime(self.get_plot_data())
                self.captured_output += f' | Loaded up to: {last_dta_time}'
                self.f_new_plot_data= True
                # self.f_marks_resync = True  
                self._t_update_plot() 
            if DEBUG_PRINT == 1:
                print(self.captured_output )
 
    def on_get_data_button_click(self, event):
        if event.name == 'button_release_event':
            last_dta_time = pd.to_datetime(self.get_plot_data())
            self.captured_output = f'Loaded up to: {last_dta_time}' 
            self.f_new_plot_data= True
            # self.f_marks_resync = True  
            self._t_update_plot()  
        if DEBUG_PRINT == 1:
            print (self.captured_output)

    def on_save_data_button_click(self, event):
         if event.name == 'button_release_event':
            self._save_m_to_file()
            self.captured_output = f'Saved marks data in: {self.m_file}'
     
    def on_checkbox_clicked(self, label, event):
        if event.key is None:
            return
        if event.name == 'button_release_event':
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


    def _eucl_distance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
    def _save_m_to_file(self):
        # Save marks to a CSV file
        df = pd.DataFrame(self.marks, columns=['Date', 'x', 'y', 'm_idx', 'ecl_w', 'ecl_h', 'buy', 'ellipse'])
        df.to_csv(self.m_file, index=False)
        self.captured_output = f'Saved marks into: {self.m_file}'

    def _get_mark_cfg(self):
        #TODO finish the helper func
        # patches.Ellipse((x_coord, y_coord), width=ecl_w, height=ecl_h, angle=0, color=color, fill=False)

        ax_h_end = self.ax.get_ylim()[1]
        ax_h_st = self.ax.get_ylim()[0]
        ax_w = self.ax.get_xlim()[1] 
        ax_h = ax_h_end - ax_h_st
        h2w_factor = ax_h / ax_w  
        ecl_w = MARK_WIDTH
        ecl_h = h2w_factor  * 10/6 #ratio

        return ecl_h,ecl_w


class INTupdateThread(Thread):
    def __init__(self, plotter):
        super(INTupdateThread, self).__init__()
        self.plotter = plotter
        self.stop_event = threading.Event()

    def run(self):
        try:
            while not self.stop_event.is_set():
                if self.plotter.f_new_plot_data == True:
                    self.plotter._t_update_plot()
                sleep(0.1)
        except Exception as e:
            # Handle exceptions here or log them
            print(f"Thread Error: {e}")
        finally:
            print("Thread Exiting...")

    def stop(self):
        self.stop_event.set()
        


