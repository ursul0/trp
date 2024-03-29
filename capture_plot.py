import matplotlib.pyplot as plt
import mplfinance as mpf

# import mplcursors
# import matplotlib.ticker as ticker

from matplotlib.widgets import MultiCursor
import matplotlib.gridspec as gridspec

import pandas as pd
import numpy as np
from pandas import Timestamp

# from scipy.spatial import distance
import pickle

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

from data_proc import DataProc, DEF_SYMBOL, DEF_INTERVAL, TOTAL_CANDLES, SYMBOLS

#configure backend
import matplotlib

# interactive backends: GTK3Agg, GTK3Cairo, GTK4Agg, GTK4Cairo, MacOSX, nbAgg, QtAgg, QtCairo, 
#  TkAgg, TkCairo, WebAgg, WX, WXAgg, WXCairo, Qt5Agg, Qt5Cairo
# matplotlib.use('TkAgg')


#up to 2500?
# TOTAL_CANDLES = 100
ACT_MARK_WIDTH = 1.7
LBL_MARK_WIDTH = 3

# SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT']
# PERIODS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']

INTERVALS_ON_APPEND = 1

DEBUG_PRINT = 0



class CaptureOnClick:
    """ interactive plot, chart marking data collector """
    def __init__(self, path = '.\\.data\\', pair_df=None, data_proc:DataProc = None, \
                 symbol=DEF_SYMBOL, interval=DEF_INTERVAL):
        # self.fig = mpf.figure(style='yahoo',figsize=(10,6))

        # no volume plot:
        # self.fig = mpf.figure(style='charles',figsize=(10,6))
        # self.ax  = self.fig.add_subplot()
        # add volume
        # self.volume_ax = self.fig.add_subplot()
        # self.ax.label_outer()
        # self.fig.subplots_adjust(hspace=0)


        # self.fig, (self.ax, self.volume_ax) = plt.subplots(
        #                               nrows=2, 
        #                               ncols=1, 
        #                               figsize=(10, 6),
        #                               gridspec_kw={'height_ratios': [5, 1]})
         
        # self.ax.label_outer()
        # self.fig.subplots_adjust(hspace=0)

        # Adjust the position of the axes to leave space for the textboxes and the legend
        # pos :             [left, bottom, width, height] 
        # old single: self.ax.set_position([0.03, 0.22, 0.88, 0.73])
        #external axes custom config:
        # vol_h = 0.1
        # self.ax.set_position([0.03, 0.22+vol_h, 0.88, 0.73-vol_h])
        # self.volume_ax.set_position([0.03, 0.22, 0.88, vol_h]) 
        
        self.path = path
        self.pair = symbol
        self.interval = interval

        #initialize data processor
        if data_proc is None:
            self._print_debug("Provide DataProc object.")
            return
        else:
            self.dp = data_proc

        # self.pair_df = pd.DataFrame(self.data_proc.pair_df).copy(deep=True)
        self.pair_df = self.dp.pair_df
        
        self.file, self.m_file = self.dp._make_file_names_new()
        
        #debug print
        self.captured_output = ''
        
        # self.ax.set_ylabel('price')
        # self.ax.set_xlabel('time')

        #draw plot & marks
        date = self.get_plot_data()
        # self._draw_plot()

        # self.fig, self.axes = mpf.plot(self.pair_df, type='candle', style='charles',
        #         ylabel='Price',
        #         ylabel_lower='Volume',
        #         volume=True,
        #         figratio=(10,6),
        #         figscale=1.25,
        #         returnfig=True, xrotation=0, scale_padding=dict(left=0.03, right=0.97))
        
        self.fig, self.axes = mpf.plot(self.pair_df, type='candle', style='charles',
                volume=True, figratio=(10,6), figscale=1.1, returnfig=True, xrotation=0)
            
 
        # get the axes to later update the existing plot with a new data:
        self.ax = self.axes[0]
        self.volume_ax = self.axes[2]
        self._configure_axes()

        # sample plots:
        # ap = mpf.make_addplot(self.pair_df['Close'],panel=1,type='line',ylabel='Line',mav=(5,10))
        # mpf.plot(self.pair_df,mav=10,type='candle',ylabel='Candle',addplot=ap,panel_ratios=(1,1),figratio=(1,1),figscale=1.5)
              
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_pick)
        # def disconnect_callback(self):
        #     # Disconnect the callback using the connection id
        #     self.fig.canvas.mpl_disconnect(self.cid)

       # pos :             [left, bottom, width, height]    
        # Add textboxes below the axes
        textbox_pair_pos = [0.20, 0.015, 0.10, 0.05]
        # textbox_pair_pos = [0.15, 0.015, 0.12, 0.05]
        textbox_interval_pos = [0.4, 0.015, 0.05, 0.05]

        self.tb_pair = TextBox(plt.gcf().add_axes(textbox_pair_pos), 'Pair:', \
                               initial=self.pair)
        self.tb_interval = TextBox(plt.gcf().add_axes(textbox_interval_pos), 'Period:', \
                                 initial=self.interval)
        
        # Connect events to the textboxes
        self.tb_pair.on_submit(self.on_tb_pair_submit)
        self.tb_interval.on_submit(self.on_tb_interval_submit)

        # button to get new data
        button_pos = [0.65, 0.015, 0.1, 0.05] 
        self.get_data_btn = Button(plt.gcf().add_axes(button_pos), 'Get Data')
        self.get_data_btn.on_clicked(self.on_get_data_button_click)

        # button to save markings
        button_pos = [0.77, 0.015, 0.1, 0.05] 
        self.save_data_btn = Button(plt.gcf().add_axes(button_pos), 'Save Marks')
        self.save_data_btn.on_clicked(self.on_save_data_button_click)
 
        # # Create CheckButtons widget
        # self.checkbox_ax = plt.axes([0.88, 0.01, 0.1, 0.05])  #  position and size
        # self.checkbox = CheckButtons(self.checkbox_ax, labels=['INT'], actives=[False])
        # self.checkbox.on_clicked(self.on_checkbox_clicked)

        self.event = None

        # Marks:
        marks = self._load_m_from_file()
        if marks == -1:
            self.marks_store = self._create_marks_store()
        else:
            self.marks_store = marks

        self.marks_n = self.marks_store[DEF_SYMBOL]

        self._add_marks2plot()
        self._update_plot_text(date)

        # Add a crosshair
        if self._is_jupyter() == False:
            multi = MultiCursor(self.fig.canvas, (self.ax,), color='blue', lw=0.3, horizOn=True, vertOn=True)


        # plt.ioff()
        # plt.show()
        mpf.show()

    def _is_jupyter(self):
        try:
            from IPython import get_ipython

            ipython = get_ipython()

            if ipython is not None and 'IPKernelApp' in ipython.config:
                # Running in a Jupyter Notebook
                return True
            else:
                # Not running in a Jupyter Notebook
                return False

        except ImportError:
            # IPython module not found, not in a Jupyter environment
            return False


    def _configure_axes(self):
        #configure ticks & labels for the axes
        self.ax.yaxis.set_label_position("left")
        self.volume_ax.yaxis.set_label_position("left")
        self.ax.tick_params(axis='y', labelleft=True, labelright=False, left=True, right=False)
        self.volume_ax.tick_params(axis='y', labelleft=True, labelright=False, left=True, right=False)

        # plt.subplots_adjust(left=0.01, right=0.99)


        # Adjust the layout for tight plotting
        # plt.subplots_adjust(left=0.05, bottom=0.1, right=0.95, top=0.9, wspace=0, hspace=0)
        # plt.subplots_adjust(left=0.01)
        
        # self.fig.tight_layout()
        # self.fig.subplots_adjust(hspace=0)
        # self.fig.subplots_adjust(left=0.01, right=0.99) 
        
        # self.ax.set_ylabel('Price')
        # self.volume_ax.set_ylabel('Volume')
        

    def get_plot_data(self):   
        pair_df, pair, interval = self.dp.get_data(self.pair, self.interval, refresh = True, savedata = False)
        # sleep(0.01)
        self.pair_df = pair_df#.copy(deep=True)

        return pd.to_datetime(self.pair_df.index[-1]) 
    
    def refresh_plot_data(self):   
        #pair, interval == self.pair, self.interval if works as it should
        pair_df, pair, interval = self.dp.get_upd_data(self.pair, self.interval)

        self.pair_df = pair_df    #.copy(deep=True) if we want to allocate a copy
        #returns datetime of the data tail entry 
        return pd.to_datetime(self.pair_df.index[-1])
     
 
    def _create_marks_store(self):
            marks_store = {}
            for pair in SYMBOLS: 
                # marks_store[pair] = pd.DataFrame(columns=['date', 'price', 'x', 'y', 'kind', 'color', 'obj'])
                marks_store[pair] = pd.DataFrame(columns=['date', 'price', 'x',  'kind', 'color', 'obj'])
               
            return marks_store

    def _add_marks2plot(self):
        marks = self.marks_n
        if not marks.empty:
            # try:
            # for mark_entry in self.marks_n 
            for index, row in marks.iterrows():
                # if sync == True: #resync of marks is required:
                date = row['date']
                price = row['price']
                color = row['color']
                kind = row['kind']

                #find current plot x coordinate for the mark
                dfp = self.pair_df
                nearest_timestamp = dfp.index.asof(date)
                if pd.isna(nearest_timestamp):
                    self.captured_output = f'mark at {date} is outside of the axes data'
                    self._print_debug(self.captured_output)
                    continue

                # x_coord = dfp.index.get_loc(nearest_timestamp)
                
                # Find the next occurrence where the mark 'price' is between 'Low' and 'High' 
                # in case we moved from larger to smaller period and need to find the correct candle
                next_occurrence = dfp[(dfp.index >= nearest_timestamp) & (dfp['Low'] <= price) & (dfp['High'] >= price)].iloc[0]
                x_coord = dfp.index.get_loc(next_occurrence.name) #.name returns associated index label
                self.captured_output = f'date: {date}, x_coord: {x_coord}'
                
                obj_cl = self._draw_ellipse(x_coord, price, color, kind)
                
                if next_occurrence.name > date:
                    #we found more presice candle location, on a lower interval. update the mark
                    marks.at[index, 'date'] = next_occurrence.name

                marks.at[index, 'x'] = x_coord
                marks.at[index, 'obj'] = obj_cl

                # else:    
                #     obj_cl = row['obj'] 
                #     if obj_cl is not None:
                #         self.ax.add_patch(obj_cl) 
        
            # except IndexError:
            #     self._print_debug(f'self.marks_n is empty!')
        
        # return index
      

    def _print_debug(self, text):
            """
            Assigns the given text to self.captured_output and prints it if DEBUG_PRINT is 1.
            
            Parameters:
            - text (str): The text to be assigned to self.captured_output and printed.
            """
            self.captured_output = text
            if DEBUG_PRINT == 1:
                print(self.captured_output)

    #update plot
    def _t_update_plot(self, date):
 
        # if self.run_refresh_flag == True:
        #     self.refresh_plot_data()

        self._redraw_plot() #add processing of the last candle + maybe add ticker

        self._add_marks2plot()

        # if self.f_marks_resync == True:
        #     self._add_marks2plot(sync=True)
        # else:
        #     self._add_marks2plot(sync=False)

        self._update_plot_text(date) #kk for now
        self.ax.figure.canvas.draw()
      
    # def _draw_plot(self):
    #     #old, no volume:
    #     # mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500) 
    #     # self.ax.figure.canvas.draw()

    #     # self.ax.set_title(f'Interactive chart of {self.pair} {self.interval}')

    #     # mpf.plot(self.pair_df, type='candle', style='charles', volume=self.volume_ax, ax=self.ax)
    #     # mpf.plot(self.pair_df, type='candle', style='charles', volume=self.volume_ax, ax=self.ax, warn_too_much_data=2500)

    #     mpf.plot(self.pair_df,type='candle',style='charles',volume=True,figratio=(15,10))
  
    #     self.ax.figure.canvas.draw()
            
    def _redraw_plot(self):
        # no check if empty(why would it be?) and has last candle only
        if self.pair_df.shape[0] == TOTAL_CANDLES:
            # #draw new data, including new interval
            self.ax.clear()
            self.volume_ax.clear()

            # Update the plot with the new data
            mpf.plot(self.pair_df, type='candle', style='charles', volume=self.volume_ax, \
                     ax=self.ax, warn_too_much_data=2500, xrotation=0)
            
            self._configure_axes()
            # Redraw the figure
            self.fig.canvas.draw()

        #we will never get here:     
        elif self.pair_df.shape[0] == INTERVALS_ON_APPEND:
            
            
            #TODO: update only the last candle, not the whole plot 
            
 
            # self.ax.clear()
            # self.volume_ax.clear()
            
            # mpf.plot(self.pair_df, type='candle', style='charles', volume=self.volume_ax, \
            #          ax=self.ax, warn_too_much_data=2500, xrotation=0)
            
            updated_data = self.pair_df.iloc[-INTERVALS_ON_APPEND:]
            self.ax.plot(updated_data.index, updated_data['Close'], label='Close')

            # self._configure_axes()

            # Redraw the figure
            # self.fig.canvas.draw()

        else:
            self._print_debug('_redraw_plot: WTF?')
       
    def _update_plot_text(self, date):
        # self.ax.set_title(f'[Binance]:   {self.pair} | {self.interval} | {date}')
        utm = self.dp.data_map[self.pair][self.interval]['Updated']
        self.ax.set_title(f' {self.pair} | {self.interval} | Last candle: {date} | Update time: {utm}')
        #why would it be anything else, but ok:
        self.tb_pair.set_val(self.pair)
        self.tb_interval.set_val(self.interval)

    def _draw_ellipse(self, x_coord, y_coord, color, kind, fill = False):
        ax_h_end = self.ax.get_ylim()[1]
        ax_h_st = self.ax.get_ylim()[0]
        ax_w = self.ax.get_xlim()[1] 
        ax_h = ax_h_end - ax_h_st
        h2w_factor = ax_h / ax_w  
        if kind == 'ACT':
            ecl_w = ACT_MARK_WIDTH
            ecl_h = h2w_factor  * 10/8 #ratio
        elif kind =='LBL':
            ecl_w = LBL_MARK_WIDTH
            ecl_h = h2w_factor  * 10/6*2
        

        # Create an Ellipse patch with transparency
        # ellipse = patches.Ellipse(center, width, height, angle=angle, edgecolor='black', facecolor='blue', alpha=alpha)

 
        if kind == 'LBL':
            ellipse = patches.Ellipse((x_coord, y_coord), width=ecl_w, height=ecl_h, angle=0, color=color, fill=fill)
        elif kind == 'ACT': 
            ellipse = patches.Ellipse((x_coord, y_coord), width=ecl_w, height=ecl_h, angle=0, \
                                  color=color, fill=fill)
        # buy = 1 if color == 'green' else 0

        self.ax.add_patch(ellipse)

        return ellipse

        
    #Plot interactions:
    def add_rmv_plot_mark_new(self, event):
        if event.inaxes == self.ax:
            #get data coordinates:
            x_coord = event.xdata
            y_coord = event.ydata
            #figure? coordinates : event.x, event.y
            if x_coord is not None and y_coord is not None:
                valid_x_range = self.pair_df.shape[0]
                if 0<= x_coord <= valid_x_range:
                    df = self.pair_df
                    #get actual data coordinates:
                    price = y_coord
                    date = df.index[round(x_coord)]  

                    self._print_debug(f"Clicked coords: ({x_coord}, {y_coord}, date: {date})")
                    
                  
                    if event.key == 'alt' and event.button == 3:
                        # alt +right click: Remove the nearest mark on axes
                        if not self.marks_n.empty:
                            # Find target mark index
                            if len(self.marks_n) > 1:
                                # Calculate Euclidean distances 
                                max_x_diff = self.marks_n['x'].max() - self.marks_n['x'].min()
                                max_y_diff = self.marks_n['price'].max() - self.marks_n['price'].min()
             
                                normalized_distances = (((self.marks_n['x'] - x_coord) / max_x_diff) ** 2 + \
                                                        ((self.marks_n['price'] - price) / max_y_diff) ** 2) ** 0.5
                                # Find target mark index
                                target_mark_index = normalized_distances.idxmin()
                            else:
                                target_mark_index = self.marks_n.index[0]

                            # Get the mark to remove
                            row_data = self.marks_n.loc[target_mark_index]
                            ellipse_to_remove = row_data['obj']
                            # Remove the mark from the plot
                            ellipse_to_remove.remove()
                            # Remove the mark from the DataFrame
                            self.marks_n = self.marks_n.drop(target_mark_index)
                            #update marks store    
                            self.marks_store[self.pair] = self.marks_n

                            
                    elif event.button == 1 or event.button == 3:
                        kind = 'ACT'
                        color = 'green' if event.button == 1 else 'red'

                        if event.key == 'shift' and event.button == 1:
                            kind = 'LBL'
                            color = 'green'
                        if event.key == 'shift' and event.button == 3:
                            kind = 'LBL'
                            color = 'red'
                        # if event.key == 'control' and event.button == 1:
                        # if event.key == 'alt' and event.button == 3:
                            
                        #==========================================
                        df = self.marks_n                        
                        obj = self._draw_ellipse(x_coord, y_coord, color, kind)

                        # self.marks_n = pd.DataFrame(columns=['date', 'price', 'x', 'kind', 'color', 'obj'])
                        new_row = {'date': date, 'price': price, 'x': x_coord, \
                                   'kind': kind, 'color' : color, 'obj': obj}
                        #add new mark:
                        # self.marks_n = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).dropna(how='all', axis=1)
                        self.marks_n = df.reset_index(drop=True)

                        #update marks store    
                        self.marks_store[self.pair] = self.marks_n
                        
                        # df.loc[date] = new_row
               
                    self.ax.figure.canvas.draw()
                else:
                    self._print_debug("Clicked outside the valid range of indices")
            else:
                self._print_debug("Invalid coordinates")
        # Click occurred outside the axes
        else:
            self._print_debug("Clicked outside the axes")   

    #handle UI events
    def on_pick(self, event):
        # Check if the pick event occurred on the plot_ax or ui_ax
        self.event = event
        if event.inaxes == self.ax:
            self.add_rmv_plot_mark_new(event)
            
        else:
            # self.captured_output += f' on_pick(): Figure clicked at: ({event.x},{event.y}) | '
            if event.key is not None:
                self._print_debug(event)
    
    def on_tb_pair_submit(self, text): 
        
        if self.event.name != 'button_press_event' and self.event.button != '<MouseButton.LEFT: 1>':
            return

        else:
            #pair didn't change:
            if text == self.pair:
                last_dta_time = pd.to_datetime(self.refresh_plot_data())
                self.captured_output += f'Added up to: {last_dta_time}'
                #TODO: make only one vline update now?
                self.f_new_plot_data= True
                self.f_marks_resync = False  
                self._t_update_plot(last_dta_time) 
            else:
                self.pair = text #self.tb_pair.text
                self.interval = self.tb_interval.text
                last_dta_time = pd.to_datetime(self.get_plot_data())
                self.captured_output += f'Loaded up to: {last_dta_time}'
                self.f_new_plot_data= True
                self.f_marks_resync = True  
                self.marks_n = self.marks_store[self.pair]
                self._t_update_plot(last_dta_time) 

            self._print_debug(self.captured_output)
    
    def on_tb_interval_submit(self, text): 
        if self.event.name != 'button_press_event' and self.event.button != '<MouseButton.LEFT: 1>':
            return
        else:  
            #interval didn't change
            if text == self.interval:
                self.interval = text #self.tb_pair.text
                # get new data up to last_dta_time
                last_dta_time = pd.to_datetime(self.refresh_plot_data())
                #TODO: make only one vline update now
                self.captured_output = f'Added data up to: {self.interval}'
                self.f_marks_resync = False 
                #maybe pair changed, set proper marks store 
                self.marks_n = self.marks_store[self.pair]
                self._t_update_plot(last_dta_time) 
                
            else:
                #get both textboxes:
                self.interval = text
                self.pair = self.tb_pair.text
                last_dta_time = pd.to_datetime(self.get_plot_data())
                self.captured_output += f'Loaded data up to: {last_dta_time}'
                
                self.f_marks_resync = True 
                #maybe pair changed, set proper marks store 
                self.marks_n = self.marks_store[self.pair]
                self._t_update_plot(last_dta_time) 

            self._print_debug(f'Loaded on plot: {self.pair} at {self.interval} at {last_dta_time}')
 
    def on_get_data_button_click(self, event):
        # if self.event.name != 'button_press_event' and self.event.button != '<MouseButton.LEFT: 1>':
        #     return        
        if event.name == 'button_release_event':
            self.interval = self.tb_interval.text
            self.pair = self.tb_pair.text
            last_dta_time = pd.to_datetime(self.get_plot_data())
            self.captured_output = f'Loaded up to: {last_dta_time}' 
            # self.f_new_plot_data= True
            self.f_marks_resync = True  
            #maybe pair changed, set proper marks store 
            self.marks_n = self.marks_store[self.pair]
            self._t_update_plot(last_dta_time) 

        self._print_debug(self.captured_output)

    def on_save_data_button_click(self, event):
        # if self.event.name != 'button_press_event' and self.event.button != '<MouseButton.LEFT: 1>':
        #     return         
        if event.name == 'button_release_event':
            self._save_m_to_file()
            self._print_debug(f'Saved marks data in: {self.m_file}')
            
     
    # def on_checkbox_clicked(self, label):
    #     # if self.event.name != 'button_press_event' and self.event.button != '<MouseButton.LEFT: 1>':
    #     #     return
    #     if self.event.name == 'button_release_event':
    #         if label == 'INT':
    #             if self.checkbox.get_status()[0]:
    #                 self.captured_output += "stick? current plot/session. "
    #                 self.RefreshThread.run()
    #                 # self.run_refresh_flag = True
    #             else:
    #                 # deselected: Stop the INTupdateThread when interactive mode is turned off
    #                 self.RefreshThread.stop()  
    #                 # self.run_refresh_flag = False
    #                 self.captured_output = "dunno. "

    # def _eucl_distance(self, p1, p2):
    #     return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
    
    def _load_m_from_file(self):
        marks_store = -1
        if os.path.exists(self.m_file):
            with open(self.m_file, 'rb') as file:
                marks_store = pickle.load(file)
        else:
            self._print_debug(f"File '{self.m_file}' does not exist. No marks loaded.")

        return marks_store

    def _save_m_to_file(self):

        marks_store_copy = self.marks_store.copy()
        for pair in self.marks_store:
            marks_store_copy[pair]['obj'] = None
       
        # Save marks to a PKL file
        with open(self.m_file, 'wb') as file:
            # pickle.dump(self.marks_store, file)
            pickle.dump(marks_store_copy, file)
        
        self._print_debug(f'Saved marks into: {self.m_file}')



        

