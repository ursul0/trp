import matplotlib.pyplot as plt
import mplfinance as mpf

import pandas as pd
import numpy as np

import os
#from time import sleep

import datetime as dt
import matplotlib.dates as mdates

from matplotlib.widgets import Button, CheckButtons
import matplotlib.patches as patches 
#%matplotlib inline
#   %matplotlib widget
#%matplotlib notebook

MARK_WIDTH = 1.5

class plt_capture_onclick:
    """ interactive plot, chart marking data collector """
    def __init__(self, pair_df, load_filename=None, pair_name='...'):
        fig, ax = plt.subplots(figsize=(10, 6))
        self.ax = ax
        self.filename = load_filename

        self.captured_output = ''

        # pair ochl+volume data
        self.pair_df = pair_df  

        # Markings:
        self.points = []
        
        fig.canvas.toolbar_visible = False
        fig.canvas.header_visible = False
        fig.canvas.footer_visible = True
        
        ax.set_ylabel('price')
        ax.set_xlabel('time')
        ax.set_title("Interactive chart of "+ pair_name)
              
        self.cid = fig.canvas.mpl_connect('button_press_event', self.add_data)
        
        # ax.xaxis_date(tz=None)
        # ax.xaxis_date()
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Adjust the format as needed

        mpf.plot(pair_df, type='candle', ax=ax, warn_too_much_data=2500)
        # mpf.plot(pair_df, type='candle', ax=ax, warn_too_much_data=2500,mav=(7,14,50))
        
        if load_filename:
            self.load_m_from_file()

        # Create CheckButtons widget
        # self.checkbox_ax = plt.axes([0.85, 0.01, 0.1, 0.05])  #  position and size
        # self.checkbox = CheckButtons(self.checkbox_ax, labels=['MA'], actives=[False])
        # self.checkbox.on_clicked(self.on_checkbox_clicked)

        plt.show()

    
    def euclidean_distance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

    def on_checkbox_clicked(self, label):
        if label == 'MA':
            if self.checkbox.get_status()[0]:
                # Checkbox is selected, call the function to draw something
                self.draw_MA()
            else:
                # Checkbox is deselected, call the function to remove the drawing
                self.remove_MA()

    def draw_MA(self):
        # This is just a placeholder function, you can customize it to draw something on the chart
        self.captured_output = "should draw ma on the chart"
        # mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500, mav=(50,21,7))

    def remove_MA(self):
        # This is just a placeholder function, you can customize it to remove the drawing
        self.captured_output = "should remove ma from the chart"
        # mpf.plot(self.pair_df, type='candle', ax=self.ax, warn_too_much_data=2500)


    def save_m_to_file(self):
        # Save selected points to a CSV file
        df = pd.DataFrame(self.points, columns=['date', 'x', 'y', 'm_idx', 'ecl_w', 'ecl_h', 'buy', 'ellipse'])
        df.to_csv(self.filename, index=False)
        self.marked_period_start_time = self.pair_df.index[0]

    def load_m_from_file(self):
        # Check if the file exists before loading
        if os.path.exists(self.filename):
            # Load selected points from a CSV file
            df = pd.read_csv(self.filename)

            # #draw markings from the saved overlay, fix locations on the timeline
            for index, row in df.iterrows():
                date, x, y, old_m_idx, e_w, e_h, buy = row['date'], row['x'], row['y'], row['m_idx'], row['ecl_w'], row['ecl_h'] ,row['buy']
                color = 'green' if buy == 1 else 'red'

                m_candle_time = pd.to_datetime(date)
                try:
                    new_m_candle_idx = self.pair_df.index.get_loc(m_candle_time)
                    shift = old_m_idx - new_m_candle_idx
                    x-=shift
                except KeyError:
                    print(f"Candle at {m_candle_time} is out of bounds.")
                else:
                    ellipse = patches.Ellipse((x, y), width=e_w, height=e_h, angle=0, color=color, fill=False)
                    self.points.append((date, x, y, new_m_candle_idx, e_w, e_h, buy, ellipse))
                    self.ax.add_patch(ellipse)
                
                # first_item_start_time = str(df['date'][0])
                # first_item_start_time_n = mdates.datestr2num(first_item_start_time)
                # first_item_start_time_d = mdates.num2date(first_item_start_time_n)
                # first_item_start_time= pd.to_datetime(first_item_start_time)
                
        else:
            print(f"File '{self.filename}' does not exist. No points loaded.")

    def update_dataframe(self):
        # Update DataFrame with 'buy' hot bit
        # self.pair_df['buy'] = 0

        for point in self.points:
            m_time, x, y, _,_,_,_,_ = point
          
            ##TO_DO: mark / prepare data
            # mask = (self.pair_df['time'] >= x) & (self.pair_df['time'] <= x)  # Adjust based on your DataFrame columns     
            # self.pair_df.loc[mask, 'buy'] = buy

    def add_data(self, event):
        if event.inaxes is not None:
            
            #get data coordinates:
            x_coord = event.xdata
            y_coord = event.ydata
            #plot coordinates : event.x, event.y

            if x_coord is not None and y_coord is not None:
                valid_x_range = len(self.pair_df.index)
      
                if 0<= x_coord < valid_x_range:

                    if event.key == 'shift' and event.button == 1:
                        # Shift + Left click: Remove the nearest ellipse on axes
                        if self.points:
                            distances = [self.euclidean_distance((x_coord, y_coord), (point[1], point[2])) for point in self.points]
                            nearest_ellipse_index = distances.index(min(distances))
                            # Remove the corresponding patch 
                            _, _, _, _, _, _, _, ellipse_to_remove = self.points.pop(nearest_ellipse_index)
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
                        # print(self.captured_output)

                        m_candle_idx = self.pair_df.index.get_loc(date_clicked)
            
                        color = 'green' if event.button == 1 else 'red'
                        ellipse = patches.Ellipse((x_coord, y_coord), width=ecl_w, height=ecl_h, angle=0, color=color, fill=False)
                        buy = 1 if event.button == 1 else 0
                        self.points.append((date_clicked, x_coord, y_coord, m_candle_idx, ecl_w, ecl_h, buy, ellipse))
                        self.ax.add_patch(ellipse)

                    self.ax.figure.canvas.draw()
                else:
                    self.captured_output ="Clicked outside the valid range of indices"
            else:
                self.captured_output ="Invalid click coordinates"
        # Click occurred outside the axes
        else:
            self.captured_output ="Clicked outside the axes"   
        
        # print(self.captured_output)






