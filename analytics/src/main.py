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
import illuminance
import time

globals.init()

start_time = time.time()

def load_dataset():

    filename = os.path.join("analytics/data/logs.json")
    with open(filename, 'r') as file:
        json_list = json.load(file)
        return json_list

crest = sns.color_palette("crest")
color_employee = crest.as_hex()[len(crest) // 2 - 2]
color_active_employee = crest.as_hex()[len(crest) // 2]

flare = sns.color_palette("flare")
color_customer = flare.as_hex()[len(flare) // 2 - 2]
color_approached_customer = flare.as_hex()[len(flare) // 2]

scatter_palette = {"Employee": color_employee, "Customer": color_customer}

def draw_scatterplot(all_data):
    df = all_data[current_index]
    scatter_plot = sns.scatterplot(x=df["x"], y=df["y"], hue=df["employee"], palette=scatter_palette, edgecolor=None, alpha=0.4, legend='auto', ax=ax_map)
    
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
                       cmap=cmap, fill=True, alpha=0.4, ax=ax_map)

def draw_humidity(all_data):
    if current_index >= len(all_data):
        print("Humidity index out of bound")
        return
    glue = pd.DataFrame.from_dict(all_data[current_index])
    scatter_plot = sns.scatterplot(data=glue, x='x', y='y', hue='Humidity', s=5000, palette=sns.color_palette("Blues_d", as_cmap=True), alpha=0.8, ax=ax_map, legend=False, linewidth=0)
    return scatter_plot
    
def draw_illuminance(all_data, draw_legend):
    if current_index >= len(all_data):
        print("Illuminance index out of bound")
        return
    glue = pd.DataFrame.from_dict(all_data[current_index])
    res = sns.scatterplot(data=glue, x='x', y='y', hue='illuminance', s=7000, palette=sns.color_palette("YlOrBr_d", as_cmap=True), alpha=0.7, ax=ax_map, legend=draw_legend, linewidth=0)
    if draw_legend:
        sns.move_legend(res, "upper left", bbox_to_anchor=(1, 1))
    return res

# Prepare generic data
raw_ds              = load_dataset()

# Prepare concrete data
events_at_timestamp_devices, stats_at_timestamp = devices.process_devices_events(raw_ds)

# Prepare heatmap data
global all_heatmap_data
all_heatmap_data    = devices.prepare_devices_data(events_at_timestamp_devices)
globals.SLIDER_SIZE = len(all_heatmap_data) - 1

events_at_timestamp_humidity = humidity.filter_humidity_events(raw_ds)
events_at_timestamp_illuminance = illuminance.filter_illuminance_events(raw_ds)

devices.calculate_stats_at_timestamp(events_at_timestamp_devices, stats_at_timestamp)

# Prepare illumisocity data
global all_illuminance_data
all_illuminance_data = illuminance.prepare_illuminance_data(events_at_timestamp_illuminance)

# Prepare humidity data
global all_humidity_data
all_humidity_data = humidity.prepare_humidity_data(events_at_timestamp_humidity)

end_time = time.time()

print(f"Prepared data in {end_time - start_time} seconds")


fig = plt.figure(figsize=(10, 5))
# gs = fig.add_gridspec(2, 3, width_ratios=[4, 1, 1], height_ratios=[3, 2])
gs = fig.add_gridspec(3, 2, width_ratios=[4, 1], height_ratios=[1, 1, 1])

# Plot on the first subplot (top left)
ax_map = fig.add_subplot(gs[:, 0])

ax_customers = fig.add_subplot(gs[0, 1])

ax_employees = fig.add_subplot(gs[1, 1])

ax_time = fig.add_subplot(gs[2, 1])

current_index = 0

# Load bg image
bg_image = plt.imread('analytics/data/store3.png')

def draw_background_image():    
    ax_map.imshow(bg_image,
            aspect='auto',
            extent=[globals.MIN_X, globals.MAX_X, globals.MIN_Y, globals.MAX_Y])
    ax_map.axis('off')

# Set the limits for the x and y axes to prevent the graph from changing height
ax_map.set_xlim(globals.MIN_X, globals.MAX_X)
ax_map.set_ylim(globals.MIN_Y, globals.MAX_Y)

# Add a slider for timeline navigation
slider_ax = plt.axes([0.2, 0.07, 0.65, 0.03])  # [left, bottom, width, height]
curr_time_ax = plt.axes([0.2, 0.03, 0.65, 0.03])
end_time_str = f"{globals.END_TIME:02.0f}:00"
slider = Slider(slider_ax, f"{globals.START_TIME:02.0f}:00", 0, len(all_heatmap_data) - 1, valinit=0, valstep=1, color="darkgrey")
slider.vline._linewidth = 0

# Update function for slider

def move_slider(val):
    global current_index
    current_index = val
    # print(list(stats_at_timestamp.values())[val])
    update()

def timestamp_to_time(index):
    mins_passed = index * globals.MINUTES_PER_TIMESTAMP
    hrs_passed = mins_passed // 60
    mins_passed = mins_passed % 60
    return f"{(globals.START_TIME + hrs_passed):02.0f}:{mins_passed:02.0f}"

def update():

    ax_map.clear()
    draw_background_image()

    global check_states

    if check_states['Humidity']:
        draw_humidity(all_humidity_data)
        
    if check_states['Illuminance']:
        draw_illuminance(all_illuminance_data, False)

    if check_states['Temperature']:
        draw_kdeplot(all_heatmap_data)

    if check_states['Occupancy']:
        draw_scatterplot(all_heatmap_data)
        
    ax_map.set_xlim(globals.MIN_X, globals.MAX_X)
    ax_map.set_ylim(globals.MIN_Y, globals.MAX_Y)

    stats = list(stats_at_timestamp.values())[current_index]

    ax_customers.clear()
    ax_customers.axis('off')
    ax_customers.pie([stats["approached_customers"], stats["num_customers_until_now"]], labels=["Approached customers", ""], colors=[color_approached_customer, color_customer], autopct='%.0f%%', startangle=280)
    ax_customers.axis('equal')

    ax_employees.clear()
    ax_employees.axis('off')
    ax_employees.pie([stats["active_employees"], stats["num_employees_until_now"]], labels=["Involved employees", ""], colors=[color_active_employee, color_employee], autopct='%.0f%%', startangle=280)
    ax_employees.axis('equal')

    slider.valtext.set_text(f"{globals.END_TIME}:00")
    ax_time.clear()
    ax_time.axis('off')
    avg_time = stats['avg_time']
    stats_time = f"Average visit duration: "
    stats_time += f"< {globals.MINUTES_PER_TIMESTAMP:.0f} mins" if avg_time == 0.0 else f"{(avg_time * globals.MINUTES_PER_TIMESTAMP):.0f} mins"
    stats_time += f"\nPeak time: {timestamp_to_time(stats['peak_time'][0])} - {stats['peak_time'][1]} visitors"
    stats_time += f"\nOff-peak time: {timestamp_to_time(stats['off_peak_time'][0])} - {stats['off_peak_time'][1]} visitors"
    ax_time.text(0.5, 0.5, stats_time, ha='center', va='center')
    curr_time_ax.clear()
    curr_time_ax.axis('off')
    curr_time_ax.text(0.5, 0.5, timestamp_to_time(current_index), transform=curr_time_ax.transAxes, va='center', ha='center')

    plt.draw()

slider.on_changed(move_slider)

check_states = {'Humidity': False, 'Illuminance': False, 'Temperature': False, 'Occupancy': False}
check_ax = plt.axes([0.05, 0.4, 0.1, 0.15])  # [left, bottom, width, height]
checkboxes = CheckButtons(check_ax, check_states.keys(), check_states.values())

def toggle_checkbox(label):
    check_states[label] = not check_states[label]
    update()

checkboxes.on_clicked(toggle_checkbox)

update()

plt.show()