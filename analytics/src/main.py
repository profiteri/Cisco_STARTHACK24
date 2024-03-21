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
#import illuminance

globals.init()

def load_dataset():

    filename = os.path.join("../../data/logs.json")
    with open(filename, 'r') as file:
        json_list = json.load(file)
        return json_list

crest = sns.color_palette("crest")
color_employee = crest.as_hex()[len(crest) // 2 - 2]

flare = sns.color_palette("flare")
color_customer = flare.as_hex()[len(flare) // 2 - 2]

scatter_palette = {"Employee": color_employee, "Customer": color_customer}

def draw_scatterplot(all_data):
    df = all_data[current_index]
    scatter_plot = sns.scatterplot(x=df["x"], y=df["y"], hue=df["employee"], palette=scatter_palette, edgecolor=None, alpha=0.4, legend='auto', ax=ax)
    
    ### All this crap just to make sure that legend always looks the same...
    handles, labels = scatter_plot.get_legend_handles_labels()
    # Create a dictionary mapping labels to handles
    label_to_handle = dict(zip(labels, handles))
    # Sort the labels
    sorted_labels = sorted(labels)
    # Get sorted handles based on sorted labels
    sorted_handles = [label_to_handle[label] for label in sorted_labels]
    # Update the legend with the sorted handles and labels
    scatter_plot.legend(sorted_handles, sorted_labels, loc='upper left')

    return scatter_plot

def draw_kdeplot(all_data, value_x='x', value_y='y', cmap='Reds'):
    return sns.kdeplot(data=all_data[current_index], x=value_x, y=value_y,
                       bw_adjust=0.2, levels=20,
                       clip=((globals.MIN_X, globals.MAX_X), (globals.MIN_Y, globals.MAX_Y)), common_norm=False,
                       cmap=cmap, fill=True, alpha=0.4, ax=ax)

def draw_humidity(all_data):
    if current_index >= len(all_data):
        print("Humidity index out of bound")
        return
    glue = pd.DataFrame.from_dict(all_data[current_index])
    scatter_plot = sns.scatterplot(data=glue, x='x', y='y', hue='Humidity', s=300, palette=sns.color_palette("ch:s=.25,rot=-.25", as_cmap=True), alpha=0.3, ax=ax, legend=False, linewidth=0)
    return scatter_plot
    
def initialize_illuminance(all_illuminance_data, ax):

    df_illuminance = pd.DataFrame(all_illuminance_data)

    sc = ax.scatter(df_illuminance['x'], df_illuminance['y'], s=df_illuminance['illum'], c='yellow', alpha=0.6, edgecolors='none')
    
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

import illuminance
# Prepare illumisocity data
global all_illuminance_data
all_illuminance_data = illuminance.prepare_illuminance_data(raw_ds)

# Prepare humidity data
global all_humidity_data
all_humidity_data = humidity.prepare_humidity_data(events_at_timestamp_humidity)

# Create the initial figure and axis
fig, ax = plt.subplots()
current_index = 0

# Load bg image
bg_image = plt.imread('../data/test_background.png')

def draw_background_image():    
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

    ax.clear()
    draw_background_image()

    global check_states

    if check_states['Humidity']:
        draw_humidity(all_humidity_data)
        
    if check_states['Illuminance']:
        initialize_illuminance(all_illuminance_data, ax)

    if check_states['Temperature']:
        draw_kdeplot(all_heatmap_data)

    if check_states['Occupation']:
        draw_scatterplot(all_heatmap_data)
        
    ax.set_xlim(globals.MIN_X, globals.MAX_X)
    ax.set_ylim(globals.MIN_Y, globals.MAX_Y)
    plt.draw()

slider.on_changed(move_slider)

check_states = {'Humidity': False, 'Illuminance': False, 'Temperature': False, 'Occupation': False}
check_ax = plt.axes([0.05, 0.4, 0.1, 0.15])  # [left, bottom, width, height]
checkboxes = CheckButtons(check_ax, check_states.keys(), check_states.values())

def toggle_checkbox(label):
    check_states[label] = not check_states[label]
    update()

checkboxes.on_clicked(toggle_checkbox)

update()

plt.show()