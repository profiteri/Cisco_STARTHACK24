import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl
import pandas as pd
import os
import json
from matplotlib.widgets import Slider
from matplotlib.widgets import CheckButtons
import pandas as pd
import matplotlib
import globals
import devices
import humidity
#import illuminocity

globals.init()

def load_dataset():

    filename = os.path.join("../data/logs_short.json")
    with open(filename, 'r') as file:
        json_list = json.load(file)
        return json_list

def draw_scatterplot(all_data):
    pal = sns.color_palette("flare")
    c = pal.as_hex()[len(pal) // 2 - 2]
    return sns.scatterplot(data=all_data[current_index], x="x", y="y", color=c, edgecolor=None, alpha=0.4, ax=ax)

def draw_kdeplot(all_data, value_x='x', value_y='y', cmap='Reds'):
    return sns.kdeplot(data=all_data[current_index], x=value_x, y=value_y,
                       bw_adjust=0.2, levels=20,
                       clip=((globals.MIN_X, globals.MAX_X), (globals.MIN_Y, globals.MAX_Y)), common_norm=False,
                       cmap=cmap, fill=True, alpha=0.4, ax=ax)

def draw_humudity(all_data, draw_legend):
    if current_index >= len(all_data):
        print("Humidity index out of bound")
        return
    glue = pd.DataFrame.from_dict(all_data[current_index])
    res = sns.scatterplot(data=glue, x='x', y='y', hue='Humidity', s=300, palette=sns.color_palette("ch:s=.25,rot=-.25", as_cmap=True), alpha=0.3, ax=ax, legend=draw_legend, linewidth=0)
    if draw_legend:
        sns.move_legend(res, "upper left", bbox_to_anchor=(1, 1))
    return res
    
def initialize_illuminocity(all_illuminocity_data, ax):

    df_illuminocity = pd.DataFrame(all_illuminocity_data)

    sc = ax.scatter(df_illuminocity['x'], df_illuminocity['y'], s=df_illuminocity['illum'], c='yellow', alpha=0.6, edgecolors='none')
    
    return sc
# Prepare generic data
raw_ds              = load_dataset()

# Prepare concrete data
events_at_timestamp_devices = devices.process_devices_events(raw_ds)
events_at_timestamp_humidity = humidity.filter_humidity_events(raw_ds)

connection_matrix = devices.build_connection_matrix(events_at_timestamp_devices)
devices.analyze_connection_matrix(connection_matrix)

# Prepare heatmap data
global all_heatmap_data
all_heatmap_data    = devices.prepare_devices_data(events_at_timestamp_devices)

import illuminocity
# Prepare illumisocity data
global all_illuminocity_data
all_illuminocity_data = illuminocity.prepare_illuminocity_data(raw_ds)

# Prepare humidity data
global all_humidity_data
all_humidity_data = humidity.prepare_humidity_data(events_at_timestamp_humidity)

# Create the initial figure and axis
fig, ax = plt.subplots()
current_index = 0

# Load bg image
bg_image = plt.imread('../data/test_background.png')

# Plot the background image
ax.imshow(bg_image,
        aspect='auto',
        extent=[globals.MIN_X, globals.MAX_X, globals.MIN_Y, globals.MAX_Y])
ax.axis('off')

# Set the limits for the x and y axes to prevent the graph from changing height
ax.set_xlim(globals.MIN_X, globals.MAX_X)
ax.set_ylim(globals.MIN_Y, globals.MAX_Y)

# Add a slider for timeline navigation
slider_ax = plt.axes([0.2, 0.04, 0.65, 0.03])  # [left, bottom, width, height]
slider = Slider(slider_ax, 'Timeline', 0, len(all_heatmap_data) - 1, valinit=0, valstep=1, color="darkgrey")
slider.vline._linewidth = 0

# Update function for slider

def move_slider(val):
    global current_index
    current_index = val
    update()

def update():

    for artist in ax.collections:
        artist.remove()

    global check_states

    if check_states['Humidity']:
        if globals.HUMIDITY_INITIALIZED == False:
            draw_humudity(all_humidity_data, False)
            globals.HUMIDITY_INITIALIZED = True
        else:
            draw_humudity(all_humidity_data, False)
        
    if check_states['Illuminocity']:
        initialize_illuminocity(all_illuminocity_data, ax)

    if check_states['Temperature']:
        draw_kdeplot(all_heatmap_data)

    if check_states['Occupation']:
        draw_scatterplot(all_heatmap_data)
        
    ax.set_xlim(globals.MIN_X, globals.MAX_X)
    ax.set_ylim(globals.MIN_Y, globals.MAX_Y)
    plt.draw()

slider.on_changed(move_slider)

check_states = {'Humidity': False, 'Illuminocity': False, 'Temperature': False, 'Occupation': False}
check_ax = plt.axes([0.05, 0.4, 0.1, 0.15])  # [left, bottom, width, height]
checkboxes = CheckButtons(check_ax, check_states.keys(), check_states.values())

def toggle_checkbox(label):
    check_states[label] = not check_states[label]
    update()

checkboxes.on_clicked(toggle_checkbox)

plt.show()