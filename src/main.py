import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl
import os
import json
from matplotlib.widgets import Slider
import pandas as pd
import matplotlib
import globals
import heatmap

globals.init()

def load_dataset():

    filename = os.path.join("data/logs.json")
    with open(filename, 'r') as file:
        json_list = json.load(file)
        return json_list

def draw_scatterplot(all_data):
    pal = sns.color_palette("flare")
    c = pal.as_hex()[len(pal) // 2 - 2]
    return sns.scatterplot(data=all_data[current_index], x="x", y="y", color=c, edgecolor=None, alpha=0.4, ax=ax)

def draw_kdeplot(all_data, data_key='current_index', value_x='x', value_y='y', cmap='Reds'):
    return sns.kdeplot(data=all_data[data_key], x=value_x, y=value_y,
                       bw_adjust=0.2, levels=20,
                       clip=((globals.MIN_X, globals.MAX_X), (globals.MIN_Y, globals.MAX_Y)), common_norm=False,
                       cmap=cmap, fill=True, alpha=0.4, ax=ax)

def initialize_heatmap(all_data, ax, bg_image):

    # Plot the background image
    ax.imshow(bg_image,
              aspect='auto',
              extent=[globals.MIN_X, globals.MAX_X, globals.MIN_Y, globals.MAX_Y])

    # Plot the initial KDE plot
    # Assuming 'all_data' is a list of data frames, one for each 'current_index'.
    # We need to pass an integer index to access the data frame for the initial plot.
    current_index = 0
    draw_kdeplot(all_data, data_key=current_index)

    ax.axis('off')
    
def initialize_illuminocity(all_illuminocity_data, ax):
    # Assuming 'all_illuminocity_data' is a list of dictionaries with 'x', 'y', and 'illum' keys
    # where 'illum' represents the illuminance value.
    # This function will create a scatter plot overlaying the heatmap to represent illuminance data.
    
    # Convert the list of dictionaries to a DataFrame for easier manipulation
    df_illuminocity = pd.DataFrame(all_illuminocity_data)
    
    # Create a scatter plot using the 'illum' column as the size of the points
    # to visually represent the intensity of the illuminance.
    sc = ax.scatter(df_illuminocity['x'], df_illuminocity['y'], s=df_illuminocity['illum'], c='yellow', alpha=0.6, edgecolors='none')
    
    return sc
# Prepare generic data
raw_ds              = load_dataset()

# Prepare concrete data
events_at_timestamp_heatmap = heatmap.filter_heatmap_events(raw_ds)

# Prepare heatmap data
global all_heatmap_data
all_heatmap_data    = heatmap.prepare_heatmap_data(events_at_timestamp_heatmap)

import illuminocity
# Prepare illumisocity data
global all_illuminocity_data
all_illuminocity_data = illuminocity.prepare_illuminocity_data(raw_ds)

# Prepare humidity data
global all_humidity_data
# ...

# Create the initial figure and axis
fig, ax = plt.subplots()
current_index = 0

# Set the limits for the x and y axes to prevent the graph from changing height
ax.set_xlim(globals.MIN_X, globals.MAX_X)
ax.set_ylim(globals.MIN_Y, globals.MAX_Y)

# Load background image
bg_image = plt.imread('data/test_background.png')

initialize_heatmap(all_heatmap_data, ax, bg_image)

initialize_illuminocity(all_illuminocity_data, ax)

# Add a slider for timeline navigation
ax_slider = plt.axes([0.2, 0.04, 0.65, 0.03])  # [left, bottom, width, height]
slider = Slider(ax_slider, 'Timeline', 0, len(all_heatmap_data) - 1, valinit=0, valstep=1, color="darkgrey")
slider.vline._linewidth = 0

# Update function for slider
def update(val):
    if globals.HEATMAP_SELECTED:
        global current_index
        current_index = int(slider.val)

        # Remove only the KDE plot, not the background image
        for artist in ax.collections:
            artist.remove()

        # Plot the KDE plot without clearing the background image
        draw_kdeplot(all_heatmap_data, data_key=current_index)

        # Ensure the x and y limits remain the same after updating the plot
        ax.set_xlim(globals.MIN_X, globals.MAX_X)
        ax.set_ylim(globals.MIN_Y, globals.MAX_Y)
    if globals.ILLUMINOCITY_SELECTED:
        # Clear previous illuminocity scatter plot
        for artist in ax.collections:
            if isinstance(artist, matplotlib.collections.PathCollection):
                artist.remove()
            initialize_illuminocity(all_illuminocity_data, ax)

    plt.draw()

slider.on_changed(update)

plt.show()