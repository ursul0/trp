import matplotlib.pyplot as plt
import mplfinance as mpf

import pandas as pd
import numpy as np

import os
#from time import sleep
import time, datetime
import matplotlib.dates as dt

from matplotlib.widgets import Button, CheckButtons
import matplotlib.patches as patches 
#%matplotlib inline
#   %matplotlib widget
#%matplotlib notebook

MARK_WIDTH = 1.5

class plt_capture_onclick:
    """ interactive plot, chart marking data collector """
    def __init__(self, pair_df, load_filename=None, pair_name='...', flagX=True):
        fig, ax = plt.subplots(figsize=(10, 6))
        self.ax = ax
        self.filename = load_filename

        self.captured_output = ''

        # Selections
        self.points = []
        self.pair_df = pair_df  # Store the DataFrame

        fig.canvas.toolbar_visible = False
        fig.canvas.header_visible = False
        fig.canvas.footer_visible = True
        
        ax.set_ylabel('price')
        ax.set_xlabel('time')
        ax.set_title("Interactive chart of "+ pair_name)
      
        self.cid = fig.canvas.mpl_connect('button_press_event', self.add_data)
     
        if load_filename:
            self.load_from_file()

        mpf.plot(pair_df, type='candle', ax=ax, warn_too_much_data=2500)
        # mpf.plot(pair_df, type='candle', ax=ax, warn_too_much_data=2500,mav=(7,14,50))

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


    def save_to_file(self):
        # Save selected points to a CSV file
        df = pd.DataFrame(self.points, columns=['x', 'y', 'ecl_w', 'ecl_h', 'buy', 'eclipse'])
        df.to_csv(self.filename, index=False)

    def load_from_file(self):
        # Check if the file exists before loading
        if os.path.exists(self.filename):
            # Load selected points from a CSV file
            df = pd.read_csv(self.filename)
            for index, row in df.iterrows():
                x, y, e_w, e_h, buy = row['x'], row['y'], row['ecl_w'], row['ecl_h'] ,row['buy']
                color = 'green' if buy == 1 else 'red'
                ellipse = patches.Ellipse((x, y), width=e_w, height=e_h, angle=0, color=color, fill=False)
                self.points.append((x, y, e_w, e_h, buy, ellipse))
                self.ax.add_patch(ellipse)
        else:
            print(f"File '{self.filename}' does not exist. No points loaded.")

    def update_dataframe(self):
        # Update DataFrame with 'buy' hot bit
        # self.pair_df['buy'] = 0

        for point in self.points:
            x, y, _,_,_,_, = point
          
            ##TO_DO: mark / prepare data
            # mask = (self.pair_df['time'] >= x) & (self.pair_df['time'] <= x)  # Adjust based on your DataFrame columns     
            # self.pair_df.loc[mask, 'buy'] = buy

    def add_data(self, event):
        x_coord = event.xdata
        y_coord = event.ydata

        if event.key == 'shift' and event.button == 1:
            # Shift + Left click: Remove the nearest ellipse on axes
            if self.points:
                distances = [self.euclidean_distance((x_coord, y_coord), (point[0], point[1])) for point in self.points]
                nearest_ellipse_index = distances.index(min(distances))
                # Remove the corresponding patch 
                _, _, _, _, _, ellipse_to_remove = self.points.pop(nearest_ellipse_index)
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

            self.captured_output = f"Coords: ({x_coord}, {y_coord})"            
            print(self.captured_output)


            # def plottm(u): return dt.date2num(datetime.datetime.utcfromtimestamp(u))

            # # Convert a unix time u to plot time p, and vice versa
            # def plottm(u): return dt.date2num(datetime.datetime.fromtimestamp(u))
            # def unixtm(p): return time.mktime(dt.num2date(p).timetuple())
            
            # posix_epoch = datetime.datetime(1970, 1, 1)


            # chart_date = dt.num2date(x_coord).strftime('%Y-%m-%d %H:%M:%S')
            date_clicked = dt.date2num(datetime.datetime.utcfromtimestamp(x_coord))

  
            self.captured_output += f' Candle clicked at {date_clicked}'
            print(self.captured_output)

 
            color = 'green' if event.button == 1 else 'red'
            ellipse = patches.Ellipse((x_coord, y_coord), width=ecl_w, height=ecl_h, angle=0, color=color, fill=False)
            buy = 1 if event.button == 1 else 0
            self.points.append((x_coord, y_coord, ecl_w, ecl_h, buy, ellipse))
            self.ax.add_patch(ellipse)

        self.ax.figure.canvas.draw()




